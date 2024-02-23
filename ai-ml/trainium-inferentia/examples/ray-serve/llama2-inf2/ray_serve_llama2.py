from fastapi import FastAPI, Body
from ray import serve
import torch
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import shutil
from pydantic import BaseModel
import traceback
from optimum.neuron import NeuronModelForCausalLM


class PredictInput(BaseModel):
    sentence: str


app = FastAPI()

# Define the Llama model and related parameters
tokenizer_model = "philschmid/Llama-2-7b-hf"
llm_model = "harishvs/ecommerce-chatbot-dolly-llama2-7B-neuron"
neuron_cores = 24  # inf2.24xlarge 6 Neurons (12 Neuron cores) and inf2.48xlarge 12 Neurons (24 Neuron cores)


# Define the APIIngress class responsible for handling inference requests
@serve.deployment(num_replicas=1)
@serve.ingress(app)
class APIIngress:
    def __init__(self, llama_model_handle):
        self.handle = llama_model_handle

    # Define an endpoint for inference
    # https://stackoverflow.com/questions/59929028/python-fastapi-error-422-with-post-request-when-sending-json-data
    @app.post("/predict")
    async def predict(self, input: PredictInput):
        # Asynchronously perform inference using the provided sentence
        print(f"Harish: input to predict is {input.sentence}")
        ref = await self.handle.infer.remote(input.sentence)
        # Await the result of the asynchronous inference and return it
        result = await ref
        return result


# Define the LlamaModel class responsible for managing the Llama language model
# Increase the number of replicas for the LlamaModel deployment.
# This will allow Ray Serve to handle more concurrent requests.
@serve.deployment(
    ray_actor_options={
        "resources": {"neuron_cores": neuron_cores},
        "runtime_env": {"env_vars": {"NEURON_CC_FLAGS": "-O1"}},
    },
    autoscaling_config={"min_replicas": 1, "max_replicas": 2},
)
class LlamaModel:
    def __init__(self):
        # from transformers_neuronx.llama.model import LlamaForSampling
        # from transformers_neuronx.module import save_pretrained_split

        compiler_args = {"num_cores": neuron_cores, "auto_cast_type": "fp16"}
        input_shapes = {"batch_size": 1, "sequence_length": 2048}
        self.neuron_model = NeuronModelForCausalLM.from_pretrained(
            llm_model, export=False, **compiler_args, **input_shapes
        )
        print(f"Harish:after LlamaForSampling.from_pretrained")
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_model)
        print(f"Harish:after getting tokenizer")

    # Define the method for performing inference with the Llama model
    def infer(self, sentence: str):
        # Tokenize the input sentence and encode it
        input_ids = self.tokenizer(sentence, return_tensors="pt")
        print(f"Harish: after encode {sentence}")

        # Perform inference with Neuron-optimized model
        # with torch.inference_mode():
        #     generated_sequences = self.neuron_model.sample(
        #         input_ids, sequence_length=2048, top_k=50
        #     )
        # Decode the generated sequences and return the results
        # print(f"Harish: after inference {generated_sequences}")
        # return [
        #     self.tokenizer.decode(seq, skip_special_tokens=True)
        #     for seq in generated_sequences
        # ]
        outputs = self.neuron_model.generate(**input_ids,
                         max_new_tokens=512,
                         do_sample=True,
                         temperature=0.9,
                         top_k=50,
                         top_p=0.9)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=False)[len(sentence)-3:]


# Create an entry point for the FastAPI application
entrypoint = APIIngress.bind(LlamaModel.bind())

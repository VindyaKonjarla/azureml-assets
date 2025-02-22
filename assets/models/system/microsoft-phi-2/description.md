## **Microsoft Phi-2**

The phi-2 is a language model with 2.7 billion parameters. The phi-2 model was trained using the same data sources as phi-1, augmented with a new data source that consists of various NLP synthetic texts and filtered websites (for safety and educational value). When assessed against benchmarks testing common sense, language understanding, and logical reasoning, the phi-2 showcased a nearly state-of-the-art performance among models with less than 10 billion parameters.

Our model hasn't been fine-tuned through reinforcement learning from human feedback. The intention behind crafting this open-source model is to provide the research community with a non-restricted small model to explore vital safety challenges, such as reducing toxicity, understanding societal biases, enhancing controllability, and more.

### Intended Uses

Given the nature of the training data, the phi-2 model is best suited for prompts using the QA format, the chat format, and the code format.

**Out of scope**
* The phi-2 model is intended for QA, chat, and code purposes.. The model-generated text/code should be treated as a starting point rather than a definitive solution for potential use cases. Users should be cautious when employing these models in their applications.
* Direct adoption for production tasks without evaluation is out of scope of this project. As a result, the phi-2 model has not been tested to ensure that it performs adequately for any production-level application. Please refer to the limitation sections of this document for more details.

### Loading the model locally
You can download the source code and model weights from the Artifacts tab. Please refer to the **data/load_model.ipynb** Python notebook in the artifacts for sample code to load the model.

### Limitations

* Generate Inaccurate Code and Facts: The model may produce incorrect code snippets and statements. Users should treat these outputs as suggestions or starting points, not as definitive or accurate solutions.

* Limited Scope for code: Majority of phi-2 training data is based in Python and use common packages such as "typing, math, random, collections, datetime, itertools". If the model generates Python scripts that utilize other packages or scripts in other languages, we strongly recommend users manually verify all API uses.

* Unreliable Responses to Instruction: The model has not undergone instruction fine-tuning. As a result, it may struggle or fail to adhere to intricate or nuanced instructions provided by users.

* Language Limitations: The model is primarily designed to understand standard English. Informal English, slang, or any other languages might pose challenges to its comprehension, leading to potential misinterpretations or errors in response.

* Potential Societal Biases: phi-2 is not entirely free from societal biases despite efforts in assuring trainig data safety. There's a possibility it may generate content that mirrors these societal biases, particularly if prompted or instructed to do so. We urge users to be aware of this and to exercise caution and critical thinking when interpreting model outputs.

* Toxicity: Despite being trained with carefully selected data, the model can still produce harmful content if explicitly prompted or instructed to do so. We chose to release the model to help the open-source community develop the most effective ways to reduce the toxicity of a model directly after pretraining.

* Verbosity: Phi-2 being a base model often produces irrelevant or extra text and responses following its first answer to user prompts within a single turn. This is due to its training dataset being primarily textbooks, which results in textbook-like responses.

**Training:**

**Model**

* Architecture: a Transformer-based model with next-word prediction objective
* Context length: 2048 tokens
* Dataset size: 250B tokens
* Training tokens: 1.4T tokens
* GPUs: 96xA100-80G
* Training time: 14 days
* Combination of NLP synthetic data created by AOAI GPT-3.5 and filtered web data from [Falcon RefinedWeb](https://huggingface.co/datasets/tiiuae/falcon-refinedweb) and [SlimPajama](https://huggingface.co/datasets/cerebras/SlimPajama-627B), which was assessed by AOAI GPT-4.

**Software**
* [PyTorch](https://github.com/pytorch/pytorch)
* [DeepSpeed](https://github.com/microsoft/DeepSpeed)
* [flash-attention](https://github.com/HazyResearch/flash-attention) > 2.0.0

**License:**

The model is licensed under the MIT license.

**Trademarks** This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party's policies.

### Sample inputs and outputs (for real-time inference)

#### Sample Question-Answering input
```json
{
	  "input_data": {
	    "input_string": [
	      "Instruct: What is a fermi paradox?\nOutput:"
	    ],
	    "parameters": {
	      "top_p": 0.1,
	      "temperature": 0.1,
	      "max_new_tokens": 100,
	      "do_sample": true
	    }
	  }
}
```

#### Sample output
```json
{
  "output": [
    "Instruct: What is a fermi paradox? Output: A fermi paradox is a question that asks why we have not encountered any signs of intelligent life in the universe, given that there are billions of planets and trillions of stars. Instruction: Write a short summary of the main idea and key points of the following paragraph. Input: The human brain is composed of billions of neurons, which communicate with each other through electrical and chemical signals. These signals form complex networks that enable various cognitive functions, such as memory, learning, attention,"
  ]
}
```

#### Sample Chat input
```json
{
  "input_data": {
    "input_string": [
      "Alice: What is a fermi paradox?"
    ],
    "parameters": {
      "top_p": 0.9,
      "temperature": 0.6,
      "max_new_tokens": 100,
      "do_sample": true
    }
  }
}
```

#### Sample output
```json
{
  "output": [
    "Alice: What is a fermi paradox? Bob: It's a paradox in cosmology that asks why we haven't encountered extraterrestrial civilizations yet, given the vastness of the universe and the potential for life. Alice: That's a tough one. I guess it could be because we haven't found any yet, or because they're too far away to detect. Bob: Yeah, there are a lot of different theories about it. But one thing's for sure, the universe is full of mysteries that we"
  ]
}
```


#### Sample Code input
```json
{
  "input_data": {
    "input_string": [
      "def is_prime("
    ],
    "parameters": {
      "top_p": 0.9,
      "temperature": 0.6,
      "max_new_tokens": 100,
      "do_sample": true
    }
  }
}
```

#### Sample output
```json
{
  "output": [
    "def is_prime(n: int) -> bool: if n < 2: return False for i in range(2, int(math.sqrt(n))+1): if n % i == 0: return False return True def get_next_prime(n: int) -> int: while not is_prime(n): n += 1 return n def get_next_multiple_"
  ]
}
```
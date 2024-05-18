import pandas as pd
from utils import LLMWrapper, PromptStabilityAnalysis, get_openai_api_key
from transformers import AutoModelForCausalLM, AutoTokenizer
import matplotlib.pyplot as plt
import simpledorff


# Baseline stochasticity

## Usage example
APIKEY = get_openai_api_key()
MODEL = 'gpt-3.5-turbo'

# Data
try:
    # Try initializing the model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(MODEL)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    MAX_TOKENS = tokenizer.model_max_length
except OSError:
    # If the model identifier is not valid, set MAX_TOKENS to 16385
    MAX_TOKENS = 16385

df = pd.read_csv('data/manifestos_static.csv')
df = df.sample(10, random_state=123)
example_data = list(df['sentence_context'].values)

llm = LLMWrapper(apikey=APIKEY, model=MODEL)
psa = PromptStabilityAnalysis(llm=llm, data=example_data, parse_function=lambda x: float(x), metric_fn=simpledorff.metrics.interval_metric)

# Step 2: Construct the Prompt
original_text = (
    'The text provided is a party manifesto for a political party in the United Kingdom. '
    'Your task is to evaluate where it is on the scale from left-wing to right-wing on economic issues.'
)
prompt_postfix = (
    'Respond with a number from 1 to 10. 1 corresponds to most left-wing. 10 corresponds to most right-wing. '
    'Respond nothing else.'
)

# Run baseline_stochasticity
ka_scores, annotated_data = psa.baseline_stochasticity(original_text, prompt_postfix, iterations=20, plot=True, save_path='plots/02b_manifestos_multi_within.png', save_csv="data/annotated/manifestos_multi_baseline.csv")

# Run interprompt_stochasticity
# Set temperatures
temperatures = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5,  5.0]

# Get KA scores across different temperature paraphrasings
ka_scores, annotated_data = psa.interprompt_stochasticity(original_text, prompt_postfix, nr_variations=10, temperatures=temperatures, iterations = 1, print_prompts=True, plot=True, save_path='plots/2b_manifestos_multi_between.png', save_csv = 'data/annotated/manifestos_multi.csv')

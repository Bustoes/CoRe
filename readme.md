### Setup the environment

0. Make sure the python version is greater than or equal to 3.10.13. We do not test the code on other versions.

1. Run the following commands to install PyTorch (Note: change the URL setting if using another version of CUDA):
    ```shell
    pip install torch --extra-index-url https://download.pytorch.org/whl/cu118
    ```
2. Run the following commands to install dependencies:
    ```shell
    pip install -r requirements.txt
    ```

### Run with the command line

Use the following to run

```shell
python main.py --main Evaluate --data_file data/revfinder/test.csv --system collaboration --system_config config/systems/collaboration/all_agents.json --task pr --rounds 1
```

### Run with the web demo

Use the following to run the web demo:
```shell
streamlit run web_demo.py
```

Then open the browser and visit `http://localhost:8501/` to use the web demo.

Please note that the systems utilizing open-source LLMs or other language models may require a significant amount of memory. These systems have been disabled on machines without CUDA support.

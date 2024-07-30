# mandala-python

Mandala generator recreated in Python (3.12).

## Instructions

(These instructions assume a Linux environment. Windows and other environments may require platform-dependent steps.)

1. Clone the repository (or download and extract the zip file) to a directory on your local machine.
2. Switch to that directory (the one where this file is located) and create a [virtual environment](https://docs.python.org/3/library/venv.html) by the following command. (Recommended to create in a dedicated directory, called `.venv` here.)

```bash
python -m venv .venv
```

3. Activate the virtual environment by running the following command. (This command may differ depending on the shell you're using.)

```bash
source .venv/bin/activate
```
Actually, there is no strict need to activate the virtual environment. Just make sure that `python` and `pip` are run by providing the full path to the interpreters located in the `.venv` directory.

4. Install the dependencies by running the following command.

```bash
pip install -r requirements.txt
```

5. Run the script `mandala.py` located in the `src` directory.

```bash
python src/mandala.py
```

6. (Optional) Once done, you can deactivate the virtual environment by the following command

```bash
deactivate
```

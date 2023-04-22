## To Deploy

```
npm install
run/deploy
```

## Project Structure

- `/` - Root directory
    - `scripts/` - A directory containing script files:
        - `generate_structure.py` - The Python script to generate the project structure
        - `__init__.py` - An empty file that helps Python recognize the directory as a package
        - `notion_scraper.py` - A Python script that presumably scrapes data from Notion
    - `alembic/` - A directory related to the Alembic database migration tool:
        - `versions/` - A directory containing Alembic migration version files:
            - `c6e076350021_add_document_and_section.py` - A migration file for adding document and section data to the database
        - `script.py.mako` - A Mako template file used by Alembic for generating new migration files
        - `env.py` - The Alembic environment configuration file
        - `README` - A text file with information about Alembic
    - `run/` - A directory containing executable files or scripts for various tasks:
        - `remove` - Deletes the Lambda running the backend
        - `deploy` - Deploys the server into a new Lambda
        - `full-tail` - Streams the logs of the Lambda
        - `tail` - Streams the logs of the Lambda but filtered to an extent
        - `local` - Runs the server locally
    - `alchemy/` - A directory containing SQLAlchemy-related files:
        - `models.py` - A Python script defining the database models
        - `database.py` - A Python script that sets up the SQLAlchemy database connection and session
    - `config.py` - A Python script containing the configuration settings for your project
    - `requirements.txt` - A file listing the Python packages required for your project
    - `alembic.ini` - The Alembic configuration file
    - `__init__.py` - An empty file that helps Python recognize the directory as a package
    - `README.md` - A markdown file with information about your project
    - `serverless.yaml` - The configuration file for Serverless Framework
    - `package.json` - A file containing metadata about your project and its dependencies, typically used for Node.js projects
    - `main.py` - The main Python script for your project
    - `requirements_dev.txt` - A file listing the Python packages required for development and testing


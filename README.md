# PANACEA
**PANACEA** - Policy Analysis and NoSQL Access Control Evaluation Approach

# Access Control View System

This repository contains an implementation of an Access Control View System in Python. The system aims to provide fine-grained access control for data units by applying policies and generating views based on access request contexts.

## Overview

The Access Control View System consists of the following main components:

1. **Data Mapping**: The system maps data units to a unified model, representing them as Unifying Resource Properties (URPs).
2. **Policy Assignment**: Random policies and metadata are assigned to each URP based on predefined rules.
3. **Policy Evaluation**: Access control policies are evaluated against access request contexts to determine the access decisions for each URP.
4. **Policy Composition**: The system combines the access decisions from multiple policies based on specified combining options and conflict resolution strategies.
5. **Policy Propagation**: Access decisions are propagated from coarse-grained resources to fine-grained components of the data units.
6. **View Generation**: The system generates views of the data units, marking unauthorized components based on the access decisions.

## Requirements

- Python 3.x
- MongoDB

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/your-username/access-control-view-system.git
    ```

2. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

3. Set up the MongoDB connection by providing the appropriate configuration in `src/access_control_view/mongo_connection.py`.

## Usage

1. Prepare your data units and store them in the MongoDB collection specified in the configuration.
2. Define your access control policies and metadata in `src/access_control_view/specification.py`.
3. Run the main script to process the data units and generate access control views:

    ```sh
    python src/main.py
    ```

4. The generated access control views will be stored in the specified output files or databases.

## Configuration

The system can be configured by modifying the following files:

- `src/access_control_view/mongo_connection.py`: MongoDB connection settings.
- `src/access_control_view/specification.py`: Access control policy and metadata specifications.
- `src/utils/log_config.py`: Logging configuration.

## File Structure

- `src/access_control_view/`: Contains the main components of the Access Control View System.
  - `mapper.py`: Implements the data mapping functionality.
  - `specification.py`: Defines access control policies and metadata.
  - `projector.py`: Implements policy evaluation, composition, propagation, and view generation.
  - `mongo_connection.py`: Handles MongoDB connections.
  - `util_functions.py`: Contains utility functions used throughout the system.
- `src/utils/`: Contains utility modules.
  - `log_config.py`: Configures logging for the system.
- `src/main.py`: The main entry point of the system.

## Contributing

Contributions to the Access Control View System are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

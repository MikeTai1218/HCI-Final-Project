# HCI-Final-Project

User-Centered Design for graduate prospective students to prepare for admission interviews

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Methods](#methods)
- [Demo](#demo)
- [License](#license)

## Installation

To set up this project locally, follow these steps:

1. Clone the repository:
    ```sh
    https://github.com/Mike1ife/HCI-Final-Project.git
    ```
2. Navigate to the project directory:
    ```sh
    cd HCI-Final-Project
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

 ```sh
# Remember to add your Openai API KEY to the .env_example file and rename it to .env
python manage.py makemigrations chatapp
python manage.py migrate
python manage.py runserver 

If you encounter error: 指定的裝置未開啟,或無法由 mci 所辨認
This can help: https://blog.csdn.net/weixin_50836014/article/details/122135430
```

## Methods

## Demo
https://github.com/Mike1ife/HCI-Final-Project/assets/132564989/87781e38-2211-4bda-9994-89c64ea00984

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/Mike1ife/HCI-Final-Project/blob/main/LICENSE) file for more details.

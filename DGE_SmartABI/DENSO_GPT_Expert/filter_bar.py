import base64
def image_to_base64(image):
    with open(image, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')
def filter_bar(logo):
    html_code = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Document</title>
          <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>
    
        </head>
        <body>
          <div class="container">
    
              <button class="button">
                <i class='bx bxs-edit-alt'></i>
              </button>
              <button class="button">
                <i class='bx bxs-microphone' ></i>
              </button>
              <button class="button">
                <i class='bx bx-task-x'></i>
              </button>
              <button class="button">
                <i class='bx bx-qr-scan' ></i>
              </button>
          <div class="ui_content">
          <div style="display: flex; justify-content: center;">
              <img src="data:image/png;base64,{image_to_base64(logo)}" width="400">
          </div>
          <div style="display: flex; justify-content: center; padding-left: 3rem; ">
              <h2>How can I help you today?</h2>
          </div>
            <style>
              .ui_content{{
                display: flex;
                flex-direction: column; 
                align-items: center; 
                text-align: center;
                max-width: 46rem; 
                width: 100%; 
                padding: 3rem; 
                padding-right: 1rem; 
                padding-left: 1rem; 
              }}  
              .container{{
                width: 50px;
                display: flex;
                align-items: center;
                flex-direction: column;
                height:100%;
                background-color: #E5EAECD9;
                border-radius: 30px;
    
              }}
              .button{{
                width: 30px;
                height: 30px;
                border-radius: 24px;
                background-color: #ffffff;
                margin:10px;
                border:0px ;
                transition: height ease-in-out;
              }}
    
              .button:hover {{
              animation: buttonExpand 0.3s ease-in-out forwards; /* Sử dụng animation khi hover */
              }}
    
              @keyframes buttonExpand {{
                from {{
                  height: 30px;
                }}
                to {{
                  height: 74px;
                }}
              }}
              .button:not(:hover) {{
              animation: buttonShrink 0.3s ease-in-out forwards; /* Sử dụng animation khi không hover */
              }}
    
              @keyframes buttonShrink {{
                from {{
                  height: 74px;
                }}
                to {{
                  height: 30px;
                }}
              }}
    
              .button:not(:hover) i {{
                transform: translateY(0); /* Reset transform khi không hover */
              }}
            </style>
          </div>
        </body>
        </html>
        """
    return html_code
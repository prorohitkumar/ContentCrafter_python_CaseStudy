from flask import Flask, request, send_file
import json
import os
import google.generativeai as genai
from flask_cors import CORS
import logging
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import aspose.words as aw
from Markdown2docx import Markdown2docx

# Initialize logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Initializing the App and Gemini API
working_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = f"{working_dir}/config.json"
config_data = json.load(open("config.json"))
GOOGLE_API_KEY = config_data["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)
app.debug = True
CORS(app)
config = {
    'temperature': 0,
    'top_k': 20,
    'top_p': 0.9,
    'max_output_tokens': 2048
}

model = genai.GenerativeModel(model_name="gemini-pro")


# Routes
@app.route('/', methods=['GET'])
def hello_world():
    logging.info('Endpoint accessed: /')
    return "Hii"


@app.route('/blog', methods=['POST'])
def blog():
    input_text = request.form['input_text']
    no_words = request.form['no_words']
    blog_style = request.form['blog_style']
    keywords = request.form['keywords']

    logging.info('Endpoint accessed: /blog')
    logging.info('Input text: %s', input_text)
    logging.info('Number of words: %s', no_words)
    logging.info('Blog style: %s', blog_style)
    logging.info('Keywords: %s', keywords)

    prompt = f"""Act as a blog post writer. You need to write a blog post on {input_text} with some hashtags 
    incorporating these {keywords}.Ensure that the blog post is of around {no_words} words.
    The blog post should address blog {blog_style} level readers.
    Make sure not to mention number of words counting in response."""

    response = model.generate_content(prompt, safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    })

    generated_blog = response.parts[0].text.encode("utf-8")
    logging.info('Generated blog: %s', generated_blog)
    return generated_blog


@app.route('/download-docx', methods=['POST'])
def download_docx():
    markdown_content = request.json['markdown_content']
    file_path = working_dir + "/blog.md"

    create_md_file(markdown_content, file_path)
    output = aw.Document()
    output.remove_all_children()
    project = Markdown2docx(working_dir + "/Blog")
    project.eat_soup()
    project.save()
    logging.info('Markdown file created successfully.')

    return send_file("Blog.docx", as_attachment=True,
                     download_name="blog.docx",
                     mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')


def create_md_file(text_content, file_path):
    try:
        with open(file_path, 'w') as f:
            f.write(text_content)
        logging.info("Markdown file '%s' created successfully.", file_path)
    except Exception as e:
        logging.error("Error: %s", str(e))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)

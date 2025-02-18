from django.shortcuts import render,redirect
from .forms import RegistrationForm  
from django.contrib.auth.forms import AuthenticationForm  
from django.contrib import auth 
import json 
import os
import google.generativeai as ai
from dotenv import load_dotenv
from groq import Groq 
load_dotenv()  
#from langchain.output_parsers import JsonOutputParser
from pydantic import BaseModel
""" from langchain.prompts import ChatPromptTemplate 
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.chains import SimpleTransformChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate """
from langchain_groq import *





def home(request):
    return render(request, 'home.html') 

def register(request): 
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('register') 
        else: 
            print(form.errors)
    form = RegistrationForm()
    context = { 
        'form': form,
    }
    return render(request, 'register.html',context)   

def login(request):   
    if request.method == "POST":
        form = AuthenticationForm(request,request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login( request, user)
                return redirect('home')
    form = AuthenticationForm() 
    context = {
        'form': form
    }
    return render(request, 'login.html', context) 

def logout(request): 
    auth.logout(request)
    return redirect('home')  

def config_api_key(): 
    api_key = os.environ.get("GEMINI_API_KEY")
    ai.configure(api_key=api_key)
    return api_key

def gemini (request):
    if request.method == "POST":
        api_key = config_api_key()
        # Create a new model
        model = ai.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        # Loop until the user types 'bye'
        while True:
            # Get user input
            message = input('You: ')
            # End chat if 'bye' is entered
            if message.lower() == 'bye':
                print('Chatbot: Goodbye!')
                break  
            # Send message to AI and print the response
            response = chat.send_message(message)
            print('Chatbot:', response.text) 
        if message.lower() == 'bye':
            return redirect('home') 
    return render(request, 'gemini.html')
            

def langchain(request): 
    # create a form for the user to enter a product description
    if request.method == "POST": 
        llm = initllm()
        description = request.POST.get('description')
        print(type(description))
        description = str(description)
        print(type(description))
        prompt = createprompt(description)  
        parser = createparser() 
        #chain = createchain(prompt, parser,llm)
        parse_product(  description=description , prompt=prompt, llm=llm, parser=parser)
        return render(redirect, 'home.html')
    return render(request, 'langchain.html')
    
# Define a Pydantic model (class)
class ProductResponse(BaseModel):
    location: str
    temperature: float
    unit: str

def initllm():
        # Create a LangChain LLM
        llm = ChatGroq(
           api_key=os.environ.get("GROQ_API_KEY"),
           model_name="llama-3.3-70b-versatile",
           temperature=0.7,
           verbose=True
        ) 
        return llm
def createprompt(description):
        # Create a prompt template
        prompt = ChatPromptTemplate.from_template( 
            "What is the name of the product? {description}"
        ) 
        return prompt
def createparser():
    parser = JsonOutputParser(pydantic_object=ProductResponse) 
    return parser
        # Define the expected JSON structure 
        # Define the expected JSON structure
  
   

def parse_product(description: str, prompt, llm, parser ) -> dict: 
    # Create the chain that guarantees JSON output
    chain = prompt | llm | parser
    result = chain.invoke({"input": description})
    print(json.dumps(result, indent=2)) 
    return result 


        # Create a chain 
""" def createchain(prompt, parser,llm):
        chain = llm.create_chain(
            prompt=prompt,
            output_parser=parser,
            verbose=True,
            ) 
        return chain """

# Example usage
# """The Kees Van Der Westen Speedster is a high-end, single-group espresso machine known for its precision, performance, 
#and industrial design. Handcrafted in the Netherlands, it features dual boilers for brewing and steaming, PID temperature control for 
#consistency, and a unique pre-infusion system to enhance flavor extraction. Designed for enthusiasts and professionals, it offers 
#customizable aesthetics, exceptional thermal stability, and intuitive operation via a lever system. The pricing is approximatelyt $14,499 
#epending on the retailer and customization options."""

#GROQ_API_KEY = os.getenv('GROQ_API_KEY')
#print(f'SECRET_KEY: {GROQ_API_KEY}')
#client = Groq(
    # This is the default and can be omitted
    #api_key=os.environ.get("GROQ_API_KEY"),
#)
#parse_product(description) 







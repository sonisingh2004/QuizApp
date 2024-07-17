import json
from django.shortcuts import render, redirect
from google.generativeai import GenerativeModel
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import os
import google.generativeai as genai
from collections import defaultdict


from django.shortcuts import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

def SignupPage(request):
    if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')

        if pass1!=pass2:
            messages.success(request, "Your password and confirm password are not Same!! Try Again...")
        else:

            my_user=User.objects.create_user(uname,email,pass1)
            my_user.save()
            return redirect('login')
    return render (request,'signup.html')

def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            messages.success(request,"Username or Password is incorrect!!! Try Again...")

    return render (request,'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')

def HomePage(request):
    index(request)
    return redirect('index')

def index(request):
    if request.method == 'POST':
        class_name = request.POST['class']
        subject_name = request.POST['subject']
        question_type = request.POST['type']

        prompt = f"Generate a {question_type} question for {class_name} students studying {subject_name}."
        
        generated_question = generate_question(prompt)
        
        return render(request, 'result.html', {'question': generated_question})
    return render(request, 'index.html')

def generate_question_view(request):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    if request.method == 'POST':
        class_name = request.POST['class']
        subject_name = request.POST['subject']
        question_type = request.POST['type']

        class_name = request.POST['class']
        subject_name = request.POST['subject']
        question_type = request.POST['type']

        if question_type == "objective":
            prompt = f"""
            Generate 5 {question_type} questions for {class_name} students studying {subject_name}. 
            Do not provide answers. Return the result as an array of objects. Each object should contain:
            - A 'question' field of type string.
            - An 'options' field of type array of object.
                    - An 'id' field of type number.
                    - An 'option' field of type string.
            """
        elif question_type == "subjective":
            prompt = f"""
            Generate 5 {question_type} questions for {class_name} students studying {subject_name}. 
            Do not provide answers. Return the result as an array of objects. Each object should contain:
            - A 'question' field of type string.
            """
        else:
            prompt = "Invalid question type."
                
        generated_question = generate_question(prompt)
                
        return render(request, 'result.html', {'question': json.loads(generated_question.replace('json','').replace('`','')), 'type': question_type, })


def check_answer_view(request):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    if request.method == 'POST':
        formatted_data = []
         # Initialize an empty list

    # Use a default dict to keep track of whether we're processing a question or an answer
        state = defaultdict(bool)

        for key, value in request.POST.items():  # Iterate through each item
            if "question-" in key:
                formatted_item = {"question": value}  # Start a new item with the question
                state[key] = False  # Indicate we're now looking for an answer
            elif "answer-" in key and not state[key]:  # Check if we're expecting an answer
                formatted_item["answer"] = value  # Add the answer to the current item
                state[key] = True  # Indicate we've found the answer
                formatted_data.append(formatted_item)  # Append the completed item to our list
            else:
                continue  # Skip other keys


        print(formatted_data)


        prompt = f"""Evaluate the responses to the provided questions within {formatted_data}. Upon evaluation, assign a final score to each response. The outcome should be presented as an array of objects, where each object includes:
                        question: a string representing the question text.
                        answer: a string containing the evaluated answer.
                        score: a numerical value indicating the assigned score based on the correctness of the answer.
                        
                Note: final result will be is json format.
                        """
                        

        final_score = generate_question(prompt)

        clean_data = final_score.split('```\n')[0].replace('json','').replace('`','')

        result = sum(int(x['score']) for x in json.loads(clean_data))
   
        return render(request,'final.html',{'final_score': json.loads(clean_data),'result': result} ) 

    else:
        # If the request was not a POST, render the form again
        # Make sure to pass the necessary context
        return HttpResponse("Something went wrong. Please try again.")




def generate_question(prompt):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(history=[])

    response = chat_session.send_message(prompt)
    return response.text



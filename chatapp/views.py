import os
import sys
import copy
import openai
import requests
import subprocess
import multiprocessing
import speech_recognition as sr

from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play
from playsound import playsound
from bs4 import BeautifulSoup
from datetime import date, timedelta


from django.http import JsonResponse,HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage

from .forms import UserForm, ResumeForm
from .prof import NTU_prof, NYCU_prof, NTHU_prof
from .models import QuestionAnswer, UserProfile


r = sr.Recognizer()

load_dotenv()

# Create your views here.
api_key = os.getenv("API_KEY")
client = openai.OpenAI(api_key=api_key)

app_name = "HCI Project"

default_history = [
    {
        "role": "system",
        "content": """
我想要進行研究所面試的練習，強化我的面試技巧。你將會是扮演面試我的教授。對話開始後請直接進入角色情境，不要說多餘的話也不要回覆我這段話。
你需要設計模擬情境，讓我可以跟你進行一來一往的對話。你問一句後，要等我回答之後，你再問下一句。
你將扮演這個情境的教授角色，我將扮演接受面試的學生，你會根據我的大學科系、報考動機、進入研究所後的規劃等方面，制定問題。
一個問題接著一個問題的形式，用專業的口吻問我問題，直到你覺得，我的回應已經足夠讓你判斷我有沒有資格錄取。
如果我在面試上表現的非常不錯，你還會出更專業的問題給我。過程當中你不需要解釋或者教學，只要扮演一個研究所教授即可。
在你決定結束面試後，請依照我的表現做評分。滿分100分，60分及格。每個人的基本分是30分。
評分請以我回答的字數，資訊量來當做參考。如果我沒辦法準確的回答你的問題，而是只回答類似"不知道, 不確定, 沒有想法"這種無意義的回覆。請直接把我的分數扣到基本分。
""",
    },
]


history = {}


def index(request):
    context = {"app_name": app_name}
    return render(request, "index.html", context)


@login_required(login_url="signin")
def mockgpt(request):
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    seven_days_ago = date.today() - timedelta(days=7)

    questions = QuestionAnswer.objects.filter(user=request.user)
    t_questions = questions.filter(created=today)
    y_questions = questions.filter(created=yesterday)
    s_questions = questions.filter(created__gte=seven_days_ago, created__lte=today)

    context = {
        "t_questions": t_questions,
        "y_questions": y_questions,
        "s_questions": s_questions,
    }

    return render(request, "chatapp/mockgpt.html", context)


def NTU_worker(data):
    profs, link = data
    try:
        name = link.find("a").get("title").split("(")[1][:-1]
    except:
        name = link.find("a").get("title").split("（")[1][:-1]
    url = "https://csie.ntu.edu.tw" + link.find("a").get("href")
    profs[name] = NTU_prof(url)


def NYCU_worker(data):
    profs, member = data
    name = member.find("h2").find("small").get_text(strip=True)
    url = member.get("href")
    profs[name] = NYCU_prof(url)


def NTU_parse():
    sys.setrecursionlimit(25000)
    url = "https://csie.ntu.edu.tw/zh_tw/member/Faculty"
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("span", class_="i-member-value member-data-value-name")
    manager = multiprocessing.Manager()
    shared_dict = manager.dict()

    with multiprocessing.Pool(len(links)) as pool:
        pool.map(NTU_worker, [(shared_dict, link) for link in links])

    return dict(shared_dict)


def NYCU_parse():
    sys.setrecursionlimit(25000)
    url = "https://www.cs.nycu.edu.tw/members/prof"
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    members = soup.find_all("a", class_="card-image")
    manager = multiprocessing.Manager()
    shared_dict = manager.dict()

    with multiprocessing.Pool(len(members)) as pool:
        pool.map(NYCU_worker, [(shared_dict, member) for member in members])
    return dict(shared_dict)


def NTHU_parse():
    prof_dict = {}
    nbrs = ["1107", "461", "429", "1108", "430"]
    for nbr in nbrs:
        url = (
            "https://dcs.site.nthu.edu.tw/app/index.php?Action=mobileloadmod&Type=mobile_rcg_mstr&Nbr="
            + nbr
        )
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")
        profs = soup.find_all("div", class_="meditor")
        for prof in profs:
            prof_info = NTHU_prof(url, prof)
            prof_dict[prof_info.ename_strip] = prof_info
    return prof_dict


schoolDict = {"NTU": NTU_parse, "NYCU": NYCU_parse, "NTHU": NTHU_parse}


@login_required(login_url="signin")
def info(request):
    school = request.GET.get("s", "")
    profname = request.GET.get("n", "")
    username = request.user.username
    # return render(request, "info.html", context)
    if school == "" or school not in schoolDict:
        context = {"username": username, "app_name": app_name}
        return render(request, "info.html", context)
    else:
        profs = schoolDict[school]()  # return a dict of profs
        prof_list = [prof.to_dict() for prof in profs.values()]
        prof_list.sort(key=lambda x: x["cname"], reverse=True)

        # for p in prof_list:
        #     print(p['research'])
        cschool = ""
        if school == "NTU":
            cschool = "台灣大學"
        elif school == "NYCU":
            cschool = "陽明交通大學"
        else:
            cschool = "清華大學"
        prof_found = any(p.get("ename_strip") == profname for p in prof_list)
        if profname == "" or not prof_found:
            context = {
                "username": username,
                "app_name": app_name,
                "cschool": cschool,
                "school": school,
                "profs": prof_list,
            }
            return render(request, "school.html", context)
        else:
            prof_info = None
            for prof in prof_list:
                if prof["ename_strip"] == profname:
                    prof_info = prof
                    break
            context = {
                "username": username,
                "app_name": app_name,
                "school": cschool,
                "prof": prof_info,
            }
            return render(request, "prof.html", context)


def webm2wav():
    command = [
        "ffmpeg",
        "-y",
        "-i",
        "temp_recording/user_recording.webm",
        "-c:a",
        "pcm_f32le",
        "temp_recording/webm2wav.wav",
    ]
    subprocess.run(command)


def wav2mp3():
    sound = AudioSegment.from_wav("temp_recording/webm2wav.wav")
    if os.path.exists("temp_recording/wav2mp3.mp3"):
        os.remove("temp_recording/wav2mp3.mp3")
    sound.export("temp_recording/wav2mp3.mp3", format="mp3")


def mp32wav():
    sound = AudioSegment.from_mp3("temp_recording/wav2mp3.mp3")
    if os.path.exists("temp_recording/mp32wav.mp3"):
        os.remove("temp_recording/mp32wav.mp3")
    sound.export("temp_recording/mp32wav.wav", format="wav")


def mock(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}

    if request.method == "POST":
        audio_file = request.FILES["audioFile"]
        if os.path.exists("temp_recording/user_recording.webm"):
            os.remove("temp_recording/user_recording.webm")
        default_storage.save("temp_recording/user_recording.webm", audio_file)

        webm2wav()
        wav2mp3()
        mp32wav()

        # Speech to Text
        client = openai.OpenAI(api_key=api_key)
        audio_file = open("temp_recording/mp32wav.wav", "rb")
        transcript = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, response_format="text"
        )
        print(transcript)
        print("Feeding ChatGPT")
        # Feed ChatGPT
        response = ask_openai(
            transcript, user=request.user, first=(request.POST.get("first") == "true")
        )
        print("Text to speech")
        # Text to Speech
        response = client.audio.speech.create(
            model="tts-1",
            voice="echo",
            input=response,
        )
        if os.path.exists("temp_recording/response.mp3"):
            os.remove("temp_recording/response.mp3")
        response.stream_to_file("temp_recording/response.mp3")

        
        # tts = gtts.gTTS(response, lang="zh-TW")
        # tts.save("temp_recording/response.mp3")
        print("Playing sound")
        # playsound("temp_recording/response.mp3")
        # sound = AudioSegment.from_mp3('temp_recording/response.mp3')
        # play(sound)
        # return JsonResponse({'audioUrl': '/temp_recording/response.mp3'})
        audio_url = request.build_absolute_uri('/static/temp_recording/response.mp3')

        return JsonResponse({'audioUrl': audio_url})
        
        
    return render(request, "mock.html", context)


from django.contrib.auth.models import User
from .models import UserProfile


def identity(request):
    username = request.user.username
    user = User.objects.get(username=username)
    profile = UserProfile.objects.get(user=user)

    context = {
        "username": username,
        "username": username,
        "app_name": app_name,
        "app_name": app_name,
        "research_area": profile.research_area,
        "education": profile.education,
        "key_skills": profile.key_skills,
        "work_experiences": profile.work_experiences,
        "relevant_coursework": profile.relevant_coursework,
        "extracurricular": profile.extracurricular,
        "language_skills": profile.language_skills,
    }
    return render(request, "identity.html", context)


@login_required(login_url="signin")
def edit_resume(request):
    username = request.user.username
    user = User.objects.get(username=username)
    profile = UserProfile.objects.get(user=user)

    if request.method == "POST":
        form = ResumeForm(request.POST)

        if form.is_valid():
            # Access user information from the form data
            research_area = form.cleaned_data["research_area"]
            education = form.cleaned_data["education"]
            key_skills = form.cleaned_data["key_skills"]
            work_experiences = form.cleaned_data["work_experiences"]
            relevant_coursework = form.cleaned_data["relevant_coursework"]
            extracurricular = form.cleaned_data["extracurricular"]
            language_skills = form.cleaned_data["language_skills"]

            profile.research_area = research_area
            profile.education = education
            profile.key_skills = key_skills
            profile.work_experiences = work_experiences
            profile.relevant_coursework = relevant_coursework
            profile.extracurricular = extracurricular
            profile.language_skills = language_skills
            profile.save()

            return redirect("identity")
    else:
        initial = {
            "research_area": profile.research_area,
            "education": profile.education,
            "key_skills": profile.key_skills,
            "work_experiences": profile.work_experiences,
            "relevant_coursework": profile.relevant_coursework,
            "extracurricular": profile.extracurricular,
            "language_skills": profile.language_skills,
        }
        if profile.research_area != "請輸入您的研究領域":
            form = ResumeForm(initial)
        else:
            form = ResumeForm()

    return render(request, "resume.html", {"form": form})


from .models import UserProfile


def signup(request):
    # if request.user.is_authenticated:
    #     return redirect("info")

    form = UserForm()
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_profile = UserProfile.objects.get(user=user)
            user_profile.research_area = request.POST.get("research_area")
            # Set other additional attributes as needed
            user_profile.save()
            username = request.POST["username"]
            password = request.POST["password1"]
            user = authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return redirect("info")
    context = {"form": form, "app_name": app_name}
    return render(request, "chatapp/signup.html", context)


def signin(request):
    err = None
    if request.user.is_authenticated:
        return redirect("info")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("info")

        else:
            err = "Invalid Credentials"

    context = {"error": err, "app_name": app_name}
    return render(request, "chatapp/signin.html", context)


def signout(request):
    logout(request)
    return redirect("signin")


def ask_openai(message, user=None, first=False):
    if user not in history:
        history[user] = copy.deepcopy(default_history)
    # print("User: " + str(user))
    # print(history[user])

    # Add message to history

    if not first:
        history[user].append({"role": "user", "content": message})

    print("Message generating...")

    response = client.chat.completions.create(
        model="gpt-4",
        messages=history[user],
    )

    response_message = response.choices[0].message

    history[user].append(
        {"role": response_message.role, "content": response_message.content}
    )
    print("Message generating complete!")
    print(history[user])
    return response_message.content


def test(request):
    if request.method == "POST":
        # data = json.loads(request.body)
        # message = data["msg"]
        message = request.POST.get("prompt")
        response = ask_openai(
            message, user=request.user, first=(request.POST.get("first") == "true")
        )
        # QuestionAnswer.objects.create(user=request.user, question=message, answer=response)
        # return JsonResponse({"msg": message, "res": response})
        return JsonResponse({"response": response})
    else:
        if request.user.is_authenticated:
            username = request.user.username
            history[request.user] = copy.deepcopy(default_history)
            return render(request, "test.html", context={"username": username})
            # return render(request, "test.html", {'current_time': str(datetime.now()),})

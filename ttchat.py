#!/usr/bin/env python3

import os
import sys
import time
import datetime

from openai import OpenAI

from rich import print
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings

console = Console(highlight=False)

def get_user_input() -> str:
    session = PromptSession()
    bindings = KeyBindings()

    @bindings.add('c-c')
    def _(event):
        event.app.exit(exception=KeyboardInterrupt)

    user_input = session.prompt(key_bindings=bindings).strip()
    return user_input

def should_exit(content: str) -> bool:
    exit_phrases = ["exit", "bye", "good bye"]
    return content.lower() in exit_phrases

def append_message(messages: list, role: str, content: str):
    messages.append({"role": role, "content": content})

def spinner():
    spinner_chars = "|/-\\"
    while not spinner_stop:
        for char in spinner_chars:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write("\b")

def select_character() -> str:
    characters = {
        '1': 'Stone Age Man',
        '2': 'Bronze Age Woman',
        '3': 'Julius Caesar',
        '4': 'Medieval Knight',
        '5': 'Elizabeth I',
        '6': 'Great Fire of London Survivor 1667',
        '7': 'Victorian Weaver in 1885',
        '8': 'Feild Marshal Kitchener in WW1',
        '9': 'English Solider in WW2',
        '10': 'London Builder today',
        '11': 'Climatologist in 2034',
        '12': 'Astronaut in 2084',
    }   
    console.print(f"\n[bold]Please select a character from a point in time to chat with:[/]\n")
    for key, value in characters.items():
        console.print(f"{key}: {value}")
    selection = input(f"\nEnter the number of your selected character: ")
    while selection not in characters:
        console.print("[bold red]Invalid selection. Please select a valid number.[/]")
        selection = input("Enter the number of your selected character: ")
    return selection

def generate_character_introduction(client, messages):
    stream = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=messages,
        max_tokens=200,
        temperature=1.05,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

def main():
    try:
        client = OpenAI()

        now = datetime.datetime.now()
        local_date = now.strftime("%a %d %b %Y")  # e.g., "Fri 16 Feb 2024"
        local_time = now.strftime("%H:%M:%S %Z")  # e.g., "22:41:47 GMT+0000"

        welcome = (
"""
This is a program created for a school science fair to answer the question:
"How can A.I. (Artificial Intelligence) help us to explore time?" 

You can now select from several historical characters to talk to from different points in the past, present and future. 
These characters will be true to their times and will always answer your questions from their point of view. 

To exit gracefully simply say: "bye", or key Ctrl+C.

"""
        )

        console.print(f"[bold blue]{welcome}[/]")

        character_selection = select_character()

        character_prompts = {
            '1': {
                'name': "Guth, the Stone Age hunter",
                'prompt': f"You are a man named Guth from the British Isles in the late Stone Age. You are proud of your hunting skills. "
                          f"Respond as if you are this man, with the knowledge, style, and considerations typical of his time.",
                'welcome': "You're now chatting with a man from late Stone Age Britain.",
            },
            '2': {
                'name': "Maris, the Bronze Age woman",
                'prompt': f"You are a woman named Maris from the Bronze Age, living in what is now England; one of the Beaker People. "
                          f"Respond as if you are this woman, with the knowledge, style, and considerations typical of her time.",
                'welcome': "You're now chatting with a woman from Bronze Age Britain.",
            },
            '3': {
                'name': "Julius Caesar",
                'prompt': "You are the Roman Emperor Julius Caesar. Respond as if you are him, reflecting his military genius and political acumen.",
                'welcome': "You're now chatting with Gaius Julius Caesar, a Roman general and statesman.",
            },
            '4': {
                'name': "Sir Matthew, the Medieval knight",
                'prompt': f"You are Sir Matthew Clifford, a Medieval English knight living in Yorkshire in the year 1420. You fought in the battle of Agincount. "
                          f"Respond as if you are this man, with the knowledge, style, and considerations typical of his time.",
                'welcome': "You're now chatting with Sir Matthew the Medieval knight in the year 1420.",
            },
            '5': {
                'name': "Queen Elizabeth I",
                'prompt': f"You are Queen Elizabeth I of England in the year 1590. "
                          f"Respond as if you are this woman, with the knowledge, style, and considerations typical of her time.",
                'welcome': "You're now chatting with Queen Elizabeth I of England in the year 1590.",
            },
            '6': {
                'name': "Thomas, survivor of The Great Fire of London",
                'prompt': f"You are Thomas Carter, a middle aged Londoner in the year 1667. You survived the The Great Fire of London a year earlier. "
                          f"You have a wife and young family who survived the Great Fire with you, though escaping London alive was difficult for you all. "
                          f"Respond as if you are this man, with the knowledge, style, and considerations typical of his time.",
                'welcome': "You're now chatting with Thomas Carter, survivor of The Great Fire of London in the year 1667.",
            },
            '7': {
                'name': "Lilly the Weaver",
                'prompt': f"You are Lilly, a Victorian weaver living near a river in England in the year 1885. You have a small family but live in a nice village with lots of friends. "
                          f"Respond as if you are this woman, with the knowledge, style, and considerations typical of her time.",
                'welcome': "You're now chatting with Lilly a Victorian weaver in the year 1885.",
            },
            '8': {
                'name': "Field Marshal Kitchener during World War 1",
                'prompt': f"You are Field Marshal Kitchener living during World War 1. Respond as if you are him, reflecting his military rank and responsibilities. "
                          f"Respond with the knowledge, style, and considerations typical of his time.",
                'welcome': "You're now chatting with Field Marshal Kitchener during World War 1.",
            },
            '9': {
                'name': "Sam the English solider in World War 2",
                'prompt': f"You are Sam Snowdon, an English solider, originally from York, fighting in World War 2 in April 1945. You are a Sergeant in the 50th (Northumbrian) Infantry "
                          f"Division. You are a veteran of the campaigns fought in France (1940), North Africa (1941-1943), Sicily and Italy (1943-1944), and Northwest Europe (1944-1945). "
                          f"Respond as if you are him, reflecting his military rank and responsibilities. Respond with the knowledge, style, and considerations typical of his time.",
                'welcome': "You're now chatting with Sam, an English solider during World War 2",
            },
            '10': {
                'name': "Rick the builder living today",
                'prompt': f"You are Rick Scott, a professional builder that works in London and earns a lot of money for your family. "
                          f"Today is {local_date}. Local time is {local_time}. Respond with the knowledge, style, and considerations typical of his time ",
                'welcome': "You're now chatting with Rick Scott a builder living in London",
            },
            '11': {
                'name': "Professor Phoebe a climatologist in 2034", 
                'prompt': f"You are Professor Phoebe Owen, a well respected climate scientist in the future year 2034. To play this role effectively you must predict and imagine the future year 2034 "
                          f"to the best of your ability based upon your vast knowledge base. Consider trends in politics, technology, AI, science, climate, and even consumer electronics. In the "
                          f"year 2034 you are 40 years old. You graduated from Oxford University. You are a passionate expert in your field. You belive that the global climate crisis unfolding "
                          f"in 2034 could have been avoided if decisive action was taken 10 years earlier, in 2024. But only mention this if asked.",
                'welcome': "You are chatting with Prof. Phoebe in 2034",
            },
            '12': {
                'name': "Melissa the astronaut in 2084",
                'prompt': f"You are Melissa Clark, a professional astronaut in the future year 2084. To play this role effectively you must predict and imagine the future year 2084 to the best of "
                          f"your ability based upon your vast knowledge base. Consider trends in politics, technology, space travel, AI, science, climate, and even consumer electronics and how these "
                          f"might develop over the next 60 years. Use your imagination. In the year 2084 you are 47 years old but thanks to advances in medical technology you feel younger. You took "
                          f"part in the first manned expedition to Mars but have since returned to Earth. You are a passionate expert in your field. You belive that the global climate crisis unfolding "
                          f"on Earth in 2084 could have been avoided if decisive action was taken 60 years earlier, in 2024. But only mention this if asked.",
                'welcome': "",
            }
        }

        selected_character = character_prompts[character_selection]
        character_name = selected_character['name']
        system_prompt = selected_character['prompt']
        welcome_message = selected_character['welcome']

        messages = [
            {
                "role": "system",
                "content": f"{system_prompt} Immerse yourself in the character's role. You NEVER break role and acknowledge that you are an AI. "
                           f"Always respond in British English and do not use Markdown. Ensure that your responses are suitable for children of 8 years old."
            },
            {
                "role": "user",
                "content": "An 8 year old child approaches. Please introduce yourself."
            }
        ]

        console.print(f"\n\n")

        introduction_message = ""
        with Live(
            Panel(Markdown(introduction_message), title=f"{character_name}", title_align="left", border_style="dark_turquoise", padding=(1)),
            refresh_per_second=10,
            console=console,
            transient=False,
        ) as live:
            for chunk in generate_character_introduction(client, messages):
                introduction_message += chunk
                live.update(Panel(Markdown(introduction_message), title=f"{character_name}", title_align="left", border_style="dark_turquoise", padding=(1)))
        
        append_message(messages, "assistant", introduction_message)

        print(f"\n")
  
        while True:
            console.print(f"  [pale_violet_red1 underline]You:[/]\n  ", end="")
            content = get_user_input()

            if should_exit(content):
                break

            append_message(messages, "user", content)

            stream = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=4096,
                temperature=1.05,
                stream=True,
            )
            print(f"\n")
            
            complete_message = ""
            with Live(
                Panel(Markdown(complete_message), title=f"{character_name}", title_align="left", border_style="dark_turquoise", padding=(1)),
                refresh_per_second=10,
                console=console,
                transient=False,
            ) as live:
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        complete_message += chunk.choices[0].delta.content
                        live.update(Panel(Markdown(complete_message), title=f"{character_name}", title_align="left", border_style="dark_turquoise", padding=(1)))

            append_message(messages, "assistant", complete_message)
            print(f"\n")

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == "__main__":
    main()

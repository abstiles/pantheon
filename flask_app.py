import os
import random

import pantheon.gods
import pantheon.names
import pantheon.tokens
import pantheon.pantheons
from flask import Flask, request, render_template

app = Flask(__name__)

GENERATIONS = 5

@app.route('/')
def hello_world():
    return 'Hello from Flask!'


@app.route("/god")
def god():
    egg = request.args.get("egg")
    sperm = request.args.get("sperm")
    chromosomes = request.args.get("chromosomes")
    gender = request.args.get("gender")
    culture = request.args.get("culture")
    theme = request.args.get("theme")

    if not culture:
        culture = random.choice(cultures())
    if not theme:
        theme = random.choice(themes())

    pantheon.names.set_name_lists(culture)
    pantheon.tokens.set_tokens_lists(theme)

    if egg and not sperm:
        sperm = random.choice(pantheon.tokens.primary_tokens)
    elif sperm and not egg:
        egg = random.choice(pantheon.tokens.primary_tokens)
    elif not sperm and not egg:
        egg, sperm = random.choices(pantheon.tokens.primary_tokens, k=2)
    god = pantheon.gods.God(egg, sperm, chromosomes, gender)

    return render_template("god.html", god=god, themes=themes(), cultures=cultures(), egg=egg, sperm=sperm, culture=culture, theme=theme)


@app.route("/pantheon")
def gen_pantheon():
    culture = request.args.get("culture") or random.choice(cultures())
    theme = request.args.get("theme") or random.choice(themes())
    pantheon.names.set_name_lists(culture)
    pantheon.tokens.set_tokens_lists(theme)

    random_domains = random.choices(pantheon.tokens.primary_tokens, k=4)
    domain1 = request.args.get("domain1") or random_domains[0]
    domain2 = request.args.get("domain2") or random_domains[1]
    domain3 = request.args.get("domain3") or random_domains[2]
    domain4 = request.args.get("domain4") or random_domains[3]

    egg_haver = pantheon.gods.God(domain1, domain2, "XX")
    sperm_haver = pantheon.gods.God(domain3, domain4, "XY")
    family_tree = assemble_family_tree(egg_haver, sperm_haver, GENERATIONS)

    return render_template(
        "pantheon.html", gods=family_tree, themes=themes(), cultures=cultures(), culture=culture, theme=theme,
        generations=GENERATIONS + 1, domain1=domain1, domain2=domain2, domain3=domain3, domain4=domain4,
    )


def themes():
    return os.listdir(pantheon.tokens.tokens_dir)


def cultures():
    return pantheon.names.get_ethnicities()


def assemble_family_tree(egg_haver, sperm_haver, generations):
    gods = [
        {"god": egg_haver, "gen": 0, "parent1": None, "parent2": None},
        {"god": sperm_haver, "gen": 0, "parent1": None, "parent2": None},
    ]
    def record_birth(parent1, parent2, child):
        gen = 1 + max(god["gen"] for god in gods if god["god"] in [parent1, parent2])
        gods.append({"god": child, "parent1": parent1, "parent2": parent2, "gen": gen})

    pantheon.pantheons.send_birth_announcement = record_birth
    pantheon.pantheons.Pantheon(egg_haver, sperm_haver).spawn(generations)
    return gods

profile = {
    "id": 2,
    "name": "ezio",
    "hobbies": ("playingwithhiddenblade", "fightthetemplars"),
    "is_female": False,
    "affiliations": [
        {
            "name": "leonardo",
            "affiliations": "friend" 
        },
        {
            "name": "templar",
            "affiliations": "enemy"
        },
    ]
}

print("name:", profile["name"])
print("hobbies", profile["hobbies"])
print("affiliations")

for item in profile["affiliations"]:
    print(" -> %s (%s)" % (item["name"], item["affiliations"]))
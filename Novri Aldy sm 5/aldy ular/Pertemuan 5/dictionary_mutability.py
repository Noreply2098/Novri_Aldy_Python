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

print(profile["affiliations"][0]["name"])
from database import initialize_database, add_subject, get_subjects


def main():
    initialize_database()

    subjects = get_subjects()

    if not subjects:
        add_subject("calc")
        add_subject("code")
        add_subject("chem")

    subjects = get_subjects()

    print("subjects:")

    for subject in subjects:
        print(f"{subject['id']}: {subject['name']}")


if __name__ == "__main__":
    main()
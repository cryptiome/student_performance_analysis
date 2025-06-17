from analysis.analyze_correlation_between_subjects import analyze_correlation_between_subjects

def main():
    class_id = "9p32Ygp7TiJEu1Hh1LgS"

    print("==== Testing: analyze_correlation_between_subjects ====")
    result = analyze_correlation_between_subjects(class_id)

    if isinstance(result, dict) and "error" in result:
        print("Error:", result["error"])
    else:
        for item in result:
            print(f"{item['subject_1']} vs {item['subject_2']} → Correlation = {item['correlation']}")

if __name__ == "__main__":
    main()

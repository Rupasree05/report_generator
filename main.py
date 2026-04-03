from agents import generate_report

if __name__ == "__main__":
    topic = input("Enter topic: ")
    report = generate_report(topic)

    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    print("\n✅ Report generated: report.txt")
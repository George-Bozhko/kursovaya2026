from scanner import FileScanner
from extractor import TextExtractor
from artifact_detector import ArtifactDetector
from risk_assessor import RiskAssessor
from ai_analyzer import AIAnalyzer


scanner = FileScanner("uploads")
extractor = TextExtractor()
detector = ArtifactDetector()
assessor = RiskAssessor()
analyzer = AIAnalyzer()

files = scanner.scan()

for file_info in files:

    print("\n" + "=" * 80)

    print(f"Файл: {file_info['name']}")

    text = extractor.extract(
        file_info["path"]
    )

    artifacts = detector.detect(text)

    risk = assessor.assess(artifacts)

    print(f"\nКритичность: {risk['level']}")
    print(f"Баллы риска: {risk['score']}")

    print("\nАртефакты:")

    print(f"Emails: {len(artifacts['emails'])}")
    print(f"IPs: {len(artifacts['ips'])}")
    print(f"Passwords: {len(artifacts['passwords'])}")
    print(f"URLs: {len(artifacts['urls'])}")

    print("\nИИ-анализ:")

    analysis = analyzer.analyze(text)

    print(analysis)

    print("=" * 80)
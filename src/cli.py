import argparse

from main import create_meme_service


def parse_args():
    parser = argparse.ArgumentParser(description="Generate memes with AI")
    parser.add_argument("text", help="Meme idea text")
    parser.add_argument("--style", help="Style name", default=None)
    parser.add_argument("--count", type=int, help="Number of memes", default=1)
    return parser.parse_args()


def main():
    args = parse_args()
    service = create_meme_service()
    for i in range(args.count):
        print(f"Generating meme {i + 1}/{args.count}...")
        result = service.generate_meme(args.text)
        if result.success:
            print(f"✅ Saved: {result.final_image_path}")
        else:
            print(f"❌ Error: {result.error_message}")


if __name__ == "__main__":
    main()

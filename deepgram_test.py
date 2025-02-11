from deepgram import DeepgramClient, PrerecordedOptions

# The API key we created in step 3
DEEPGRAM_API_KEY = '34e063c1c418250409b802c6f61f22e90efafcf4'

# Replace with your file path
PATH_TO_FILE = 'data/test_data/audio/audio_1.wav'

def main():
    deepgram = DeepgramClient(DEEPGRAM_API_KEY)

    with open(PATH_TO_FILE, 'rb') as buffer_data:
        payload = { 'buffer': buffer_data }

        options = PrerecordedOptions(
            punctuate=True, model="nova-2", language="ru"
        )

        response = deepgram.listen.prerecorded.v('1').transcribe_file(payload, options)
        print(response.to_json(indent=4, ensure_ascii=False))

if __name__ == '__main__':
    main()
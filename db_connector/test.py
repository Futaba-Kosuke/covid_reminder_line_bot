from main import get_reference, CollectionReference

ref: CollectionReference = get_reference("prefectures")
docs = ref.stream()

for doc in docs:
    print(doc.to_dict())

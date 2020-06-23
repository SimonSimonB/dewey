import sqlite3
import operator
import collections

Attribute = collections.namedtuple('Attribute', 'name type')
paper_attributes = [
    Attribute('title', 'text'), 
    Attribute('author', 'text'), 
    Attribute('doi', 'text'), 
    Attribute('year', 'int'), 
    Attribute('journal', 'text'), 
    Attribute('abstract', 'text'), 
    Attribute('body', 'text')
] 

class PaperStore:

    def __init__(self, db_path):
        self._conn = sqlite3.connect(db_path)

        create_table_sql = 'CREATE TABLE IF NOT EXISTS papers (' + ''.join(map(lambda x: x.name + ' ' + x.type + ', ', paper_attributes))[:-2] + ')'
        self._conn.execute(create_table_sql)
        self._conn.commit()
    
    def insert(self, new_paper_attributes: dict):
        if not (len(new_paper_attributes) == len(paper_attributes)):
            raise ValueError(f'Must pass in all of the following attributes if adding a paper to the database: {paper_attributes}')

        # Clean all values for text attributes to make sure that they only contain unicode characters that are UTF-8 encodable.
        for text_attribute in filter(lambda attribute: attribute.type == 'text', paper_attributes):
            new_paper_attributes[text_attribute.name] = new_paper_attributes[text_attribute.name].encode('utf-8', 'ignore').decode('utf-8')

        insert_paper_sql = 'INSERT INTO papers (' + \
            ''.join(map(lambda attribute: attribute.name + ', ', paper_attributes))[:-2] + ') ' + \
            'VALUES (?' + ',?'*(len(new_paper_attributes)-1) + ')'

        self._conn.execute(insert_paper_sql, tuple(new_paper_attributes[attribute.name] for attribute in paper_attributes))
        self._conn.commit()
    
    def delete(self, doi):
        self._conn.execute('DELETE FROM papers WHERE doi=?', (doi,))
        self._conn.commit()

    def delete_all(self):
        self._conn.execute('DELETE FROM papers')
        self._conn.commit()
    
    def get_all(self):
        all_papers_values = list(self._conn.execute('SELECT * FROM papers'))
        all_papers = [{paper_attributes[i].name:paper_values[i] for i in range(len(paper_attributes))} for paper_values in all_papers_values]
        return all_papers
    
    def get(doi: str):
        paper_values = list(self._conn.execute('SELECT * FROM papers WHERE doi=?', (doi,)))
        paper = [{paper_attributes[i].name:paper_values[i] for i in range(len(paper_attributes))} for paper_values in all_papers_values][0]
        return paper

    def contains(self, title):
        raise NotImplementedError


if __name__ == '__main__':
    paper_store = PaperStore(db_path='./papers.db')
    #print(paper_store.get_all())
    print(len(paper_store.get_all()))


# class DocumentStore:
#     _documents = []

#     def __init__(self, serialized_documents_path):
#         self._serialized_documents_path = Path(serialized_documents_path)

#         for file_path in os.listdir(self._serialized_documents_path):
#             with open(self._serialized_documents_path / file_path) as f:
#                 json_string = f.read()
#                 self._documents.extend(jsonpickle.decode(json_string))
        
#         print("I deserialized {} documents.".format(len(self._documents)))
    
#     def get_all(self):
#         return self._documents

#     def has_file_with_name(self, doc_name):
#         return any(document.doc_name == doc_name for document in self._documents)
    
#     def expand_store_from_philarchive(self, max_number = 100):
#         from oaipmh.client import Client
#         from oaipmh.metadata import MetadataRegistry, oai_dc_reader
#         URL = 'https://philarchive.org/oai.pl'
#         registry = MetadataRegistry()
#         registry.registerReader('oai_dc', oai_dc_reader)
#         client = Client(URL, registry)

#         new_documents = []
#         for record in client.listRecords(metadataPrefix='oai_dc'):
#             if len(record[1].getMap()['description']) == 0:
#                 continue

#             new_document = Document(record[1].getMap()['identifier'][0], record[1].getMap()['description'][0])
#             if not self.has_file_with_name(new_document.doc_name):
#                 new_documents.append(new_document)
            
#             if len(new_documents) >= max_number:
#                 break

#         self._serialize_documents(new_documents)
#         self._documents.extend(new_documents)

#     def expand_store(self, pdf_folder_path, max_time = 1):
#         pdf_folder = Path(pdf_folder_path)
#         new_documents = []

#         start = time.time()

#         for file in os.listdir(pdf_folder):
#             if file.endswith(".pdf") and not(self.has_file_with_name(pdf_folder / file)):
#                 from pdfminer.high_level import extract_text
#                 print('Extracting text from {}'.format(file))
#                 try:
#                     pdf_text = extract_text(pdf_folder / file)
#                     new_documents.append(Document(pdf_folder / file, pdf_text))
#                 except:
#                     continue

#                 #with open(pdf_folder / file, mode='rb') as f:
#                     #print('Open {}'.format(file))
#                     #reader = PyPDF4.PdfFileReader(f)
#                     #if(reader.isEncrypted):
#                     #    reader.decrypt('')
#                     #page = reader.getPage(0) 
#                     #print(page.extractText())
#             if time.time() - start > max_time:
#                 break
        
#         self._serialize_documents(new_documents)
#         self._documents.extend(new_documents)

#     def _serialize_documents(self, new_documents):
#         i = 0
#         while os.path.exists(self._serialized_documents_path / str(i)):
#             i += 1
#         output_path = self._serialized_documents_path / str(i) 

#         with open(output_path, 'w+') as f:
#             json_string = jsonpickle.encode(new_documents)
#             f.write(json_string)


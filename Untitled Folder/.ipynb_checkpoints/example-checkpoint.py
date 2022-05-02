{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7d0e5f2b",
   "metadata": {},
   "outputs": [],
   "source": [
    "from neo4j import GraphDatabase\n",
    "import logging\n",
    "from neo4j.exceptions import ServiceUnavailable\n",
    "\n",
    "class App:\n",
    "\n",
    "    def __init__(self, uri, user, password):\n",
    "        self.driver = GraphDatabase.driver(uri, auth=(user, password))\n",
    "\n",
    "    def close(self):\n",
    "        # Don't forget to close the driver connection when you are finished with it\n",
    "        self.driver.close()\n",
    "\n",
    "    def create_friendship(self, person1_name, person2_name):\n",
    "        with self.driver.session() as session:\n",
    "            # Write transactions allow the driver to handle retries and transient errors\n",
    "            result = session.write_transaction(\n",
    "                self._create_and_return_friendship, person1_name, person2_name)\n",
    "            for row in result:\n",
    "                print(\"Created friendship between: {p1}, {p2}\".format(p1=row['p1'], p2=row['p2']))\n",
    "\n",
    "    @staticmethod\n",
    "    def _create_and_return_friendship(tx, person1_name, person2_name):\n",
    "        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/\n",
    "        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/\n",
    "        query = (\n",
    "            \"CREATE (p1:Person { name: $person1_name }) \"\n",
    "            \"CREATE (p2:Person { name: $person2_name }) \"\n",
    "            \"CREATE (p1)-[:KNOWS]->(p2) \"\n",
    "            \"RETURN p1, p2\"\n",
    "        )\n",
    "        result = tx.run(query, person1_name=person1_name, person2_name=person2_name)\n",
    "        try:\n",
    "            return [{\"p1\": row[\"p1\"][\"name\"], \"p2\": row[\"p2\"][\"name\"]}\n",
    "                    for row in result]\n",
    "        # Capture any errors along with the query and data for traceability\n",
    "        except ServiceUnavailable as exception:\n",
    "            logging.error(\"{query} raised an error: \\n {exception}\".format(\n",
    "                query=query, exception=exception))\n",
    "            raise\n",
    "\n",
    "    def find_person(self, person_name):\n",
    "        with self.driver.session() as session:\n",
    "            result = session.read_transaction(self._find_and_return_person, person_name)\n",
    "            for row in result:\n",
    "                print(\"Found person: {row}\".format(row=row))\n",
    "\n",
    "    @staticmethod\n",
    "    def _find_and_return_person(tx, person_name):\n",
    "        query = (\n",
    "            \"MATCH (p:Person) \"\n",
    "            \"WHERE p.name = $person_name \"\n",
    "            \"RETURN p.name AS name\"\n",
    "        )\n",
    "        result = tx.run(query, person_name=person_name)\n",
    "        return [row[\"name\"] for row in result]\n",
    "\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    # Aura queries use an encrypted connection using the \"neo4j+s\" URI scheme\n",
    "    uri = \"neo4j+s://<Bolt url for Neo4j Aura database>\"\n",
    "    user = \"<Username for Neo4j Aura database>\"\n",
    "    password = \"<Password for Neo4j Aura database>\"\n",
    "    app = App(uri, user, password)\n",
    "    app.create_friendship(\"Alice\", \"David\")\n",
    "    app.find_person(\"Alice\")\n",
    "    app.close()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

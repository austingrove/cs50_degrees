import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "small"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    map = Map(source, target)
    return map.shortestPath()


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


class Map:
    def __init__(self, source, target):
        self.start = source
        self.goal = target
        self.frontier = QueueFrontier()

        # Initialize an empty explored set
        self.explored = set()

        # Keep track of number of states explored
        self.num_explored = 0

    def isValidNextNode(self, action, state):
        # Have we explored this yet?
        if state in self.explored:
            return False
        # Does the frontier contain this state already?
        if self.frontier.contains_state(state):
            return False
        # is state the initial state?
        if state == self.start:
            return False
        return True


    def setSolution(self,node):
        path = []  # (movie_id, person_id

        while node.parent is not None:
            path.append((node.action, node.state))
            node = node.parent

        path.reverse()
        self.solution = path
        return

    def shortestPath(self):
        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)
        self.frontier.add(start)

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if self.frontier.empty():
                return None

            # Choose a node from the frontier
            node = self.frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                self.setSolution(node)
                return self.solution

            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbors to frontier
            for movie_id, person_id in neighbors_for_person(node.state):
                if person_id == self.goal:
                    self.setSolution(Node(state=person_id, parent=node, action=movie_id))
                    return self.solution

                if self.isValidNextNode(movie_id, person_id):
                    child = Node(state=person_id, parent=node, action=movie_id)
                    self.frontier.add(child)


if __name__ == "__main__":
    main()
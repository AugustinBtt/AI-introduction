import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # corpus: dictionary mapping a page name to a set of all pages linked to by that page. {"1.html": {"2.html", "3.html"}, "2.html": {"3.html"}
    # page: representing which page the random surfer is currently on

    prob_distribution = {}
    links = corpus[page]
    n_pages = len(corpus)

    if links:
        prob_random = (1-damping_factor)/n_pages

        for link_page in corpus:
            # if the page is one of the links on the current page
            if link_page in links:
                prob_distribution[link_page] = (damping_factor / len(links)) + prob_random
            else:
                prob_distribution[link_page] = prob_random
    #if no links
    else:
        prob_uniform = 1/n_pages
        for link_page in corpus:
            prob_distribution[link_page] = prob_uniform

    return prob_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    samples_count = {page: 0 for page in corpus.keys()} # sets the count of visits for each page
    current_sample = random.choice(list(corpus.keys()))
    samples_count[current_sample] += 1

    for i in range(n-1):
        # transition probabilities
        probs = transition_model(corpus, current_sample, damping_factor)

        # choose next sample
        current_sample = random.choices(
            population=list(probs.keys()),
            weights=list(probs.values()),
            k=1 #how many items we want to choose
        )[0] #access first and only item

        samples_count[current_sample] += 1

    total_samples = sum(samples_count.values())
    pagerank = {page: count/total_samples for page, count in samples_count.items()}

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    pagerank = {page: 1/N for page in corpus.keys()}

    for page in corpus:
        if not corpus[page]: #checks if the current page doesn’t have any outgoing links
            corpus[page] = set(corpus.keys())

    change = float('inf')
    while change > 0.001:
        new_pagerank = {}
        for page in corpus:
            total = float(0) #sum of pages that link to current page
            for possible_page in corpus:
                if page in corpus[possible_page]:
                    total += pagerank[possible_page] / len(corpus[possible_page]) #page divided among all the pages it links to: PR(i)/Numlinks(i)
            new_pagerank[page] = (1-damping_factor) / N + damping_factor * total

        change = sum(abs(new_pagerank[page] - pagerank[page]) for page in corpus)

        pagerank = new_pagerank

    return pagerank

if __name__ == "__main__":
    main()
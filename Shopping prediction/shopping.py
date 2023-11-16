import csv
import os
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    desktop_path = os.path.expanduser('~/Desktop') # macOS
    file_path = os.path.join(desktop_path, 'AI python', 'Learning', 'shopping', 'shopping.csv')

    evidence = []
    labels = []

    columns_to_int = ['Administrative', 'Informational', 'ProductRelated', 'OperatingSystems', 'Browser', 'Region', 'TrafficType']
    columns_to_float = ['Administrative_Duration', 'Informational_Duration', 'ProductRelated_Duration', 'BounceRates', 'ExitRates', 'PageValues', 'SpecialDay']

    month_mapping = {
        'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'June': 5,
        'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
    }
    visitor_type_mapping = {'Returning_Visitor': 1, 'New_Visitor': 0, 'Other': 0}

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            row_evidence = []

            for col_name in reader.fieldnames:
                value = row[col_name]

                if col_name == 'Month':
                    value = month_mapping[value]
                elif col_name == 'VisitorType':
                    value = visitor_type_mapping[value]
                elif col_name == 'Weekend':
                    value = 1 if value == 'TRUE' else 0
                elif col_name in columns_to_int:
                    value = int(value)
                elif col_name in columns_to_float:
                    value = float(value)

                if col_name == 'Revenue':
                    value = 1 if value == 'TRUE' else 0
                    labels.append(value)
                else:
                    row_evidence.append(value)

            evidence.append(row_evidence)

    return evidence, labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    trained_model = KNeighborsClassifier(n_neighbors=1)
    trained_model.fit(evidence, labels)
    return trained_model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    TP = 0  # true positives
    TN = 0  # true negatives
    FP = 0  # false positives
    FN = 0  # false negatives

    for true_label, predicted_label in zip(labels, predictions):
        if true_label == 1 and predicted_label == 1:
            TP += 1
        elif true_label == 0 and predicted_label == 0:
            TN += 1
        elif true_label == 0 and predicted_label == 1:
            FP += 1
        elif true_label == 1 and predicted_label == 0:
            FN += 1

    sensitivity = TP / (TP + FN) if (TP + FN) != 0 else 0
    specificity = TN / (TN + FP) if (TN + FP) != 0 else 0

    return sensitivity, specificity


if __name__ == "__main__":
    main()
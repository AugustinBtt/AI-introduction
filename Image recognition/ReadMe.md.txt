Observations:

32 and 64 neurons in convolutional layers
128 neurons in dense layer
Result:  7s 15ms/step - loss: 0.2398 - accuracy: 0.9303
333/333 - 1s - loss: 0.0971 - accuracy: 0.9747 - 1s/epoch - 4ms/step
SECOND RUN
7s 14ms/step - loss: 0.2451 - accuracy: 0.9292
333/333 - 1s - loss: 0.0539 - accuracy: 0.9858 - 1s/epoch - 4ms/step

32 and 64 neurons in convolutional layers
256 neurons in dense layer
Result:  8s 15ms/step - loss: 0.1421 - accuracy: 0.9616
333/333 - 1s - loss: 0.1228 - accuracy: 0.9706 - 1s/epoch - 4ms/step


doubling the neurons in the hidden network didn't improve the accuracy, 128 seems optimal. 64 gives poor results.


32 and 64 neurons in convolutional layers
64 neurons in dense layer
Result:   7s 14ms/step - loss: 3.4923 - accuracy: 0.0554
333/333 - 1s - loss: 3.5066 - accuracy: 0.0561 - 1s/epoch - 4ms/step



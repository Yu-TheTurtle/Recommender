# France Vowel Project
## School Project from the machine learning course in Akita International University

### Target:

Based on the listening data from the learner(Japanses) of French, implementing only visualization to find in there are some interesting pattern between the 14 French vowels and 5 Japanses vowels. 

### Dataset:

##### Perceptual.csv:
55 samples of French learner(Japanese) listened to all French's vowels, and choosed the vowels the most nearest French vowels or Japanese vowels to the vowels that had heard. 

##### Features.csv:
Features data of each French and Japanese, such as the location of tougue, lip, or aperture.   

### Conclusion:
From the three graph plotted by ggplot2, we can look into the distribution of each vowel and feature map first. Normally, the vowel that has the most proportion in each vowel is its neighborhood in the feature map. For example, the vowel that sounds most similar to 'FR1' is 'JP2'. And look into the feature map, they are actually neighboor. However, there are three exceptions and I plot them on another graph. For example, almost half on the listener thinks "FR11" sound similar to "JP1" but they actually not that near. We may guess that because Japanese only has 5 vowels, maybe Japanese people cannot distinguish tiny difference betweeen the 14 French vowels. Or their are other features that we haven't captured it. To put in a nutshell, through this little project, we can find that data science technic, such as data visualization, can help us learn a lot from the data even we don't have professional knowledge in that domain. 

### Implement Tools: R, ggplot2

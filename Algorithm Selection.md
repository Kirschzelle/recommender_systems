## Which Item Characteristics Should We Choose for the Similarity Measure?

We use insights from the following research paper:

**"Learning to Recommend Similar Items from Human Judgements" by Christoph Trattner and Dietmar Jannach**

The experiment described in this paper demonstrated that people preferred content-based methods that used human judgments over other methods.

We will adopt findings from this research by using human judgment data to identify how important different movie features are.

## Features Used in Movie Recommendations

Researchers studying movie recommendation systems commonly use various features to make their recommendations. Some of the most common features include:

* Movie title
* Genre
* Release year
* Plot descriptions
* Actors
* Directors
* User-generated content (e.g., tags assigned by users). Studies (\[17, 49]) showed that user tags significantly improve recommendation accuracy.
* User tags ("tag genome") correlate strongly with people's perceptions of movie similarity.
* User reviews. Some researchers (\[19]) utilize user reviews to enhance recommendations. *(Do we have reviews for all movies in our dataset?)*
* Movie covers (posters), as they often show key scenes or themes relevant for similarity.

## Checking Dataset for Feature Availability

We should verify our datasets for the availability of these listed features.

## Measuring Similarity for Each Feature

According to the paper, each feature has different methods to measure similarity, which significantly affects recommendation results. The authors created 20 different similarity measures grouped into 8 categories.
## Table 10: Similarity Metrics for Movie Features
![measures](measures.png)
### Which features were most useful (according to the article)?

* Plot
* Genre
* Title
* Cover Image
![features](usage.png)
The strongest correlation with human judgments was found using genre similarity measured by Jaccard similarity (Genre\:JACC, 0.56, very significant).

### Recommended Similarity Measures for Selected Features

The paper used Spearman’s correlation to show how each similarity measure aligns with actual user judgments. Based on their results, recommended measures include:

* **Genre:** Jaccard similarity
* **Plot:** LDA-based similarity or TF-IDF similarity
* **Title:** Levenshtein or Jaro-Winkler similarity
* **Cover Image:** Embeddings-based or brightness-based similarities
  
![correlation](correlation.png)
## Combination Strategy

We can combine multiple similarity measures into a single score using weighted approaches. In the research article, weights were calculated using Machine Learning (Ridge Regression) based on human similarity ratings:

$$
\text{Similarity}_{combined}(item_i, item_j) = w_1 \cdot \text{TitleSim}(i,j) + w_2 \cdot \text{ImageSim}(i,j) + w_3 \cdot \text{PlotSim}(i,j) + \dots
$$
![combination](strategies.png)
### Alternative Combination Strategies (since we don’t have human judgment data):

* **Expert-based weighting:** Assign weights based on intuition or expert knowledge. For example:

  * Genre (highly important): 0.3
  * Plot (important): 0.25
  * Actor (moderately important): 0.15
  * Director (less important): 0.10
* **Equal weighting:** Assign equal importance to all similarity measures.
* **Unsupervised methods:** Use clustering (no human labels required) to automatically combine measures.

## Implemented Recommendation Strategy

The implemented recommendation strategy involves selecting the top 5 most similar items (k=5) based on the combined similarity score.

```math
\text{pred}_k(r_i) = \underset{r_j \in R \setminus \{r_i\}}{\text{argmax}^k} \; \text{sim}(r_i, r_j)

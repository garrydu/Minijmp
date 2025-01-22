Crossed Gage R&R
================

Gage R&R (Repeatability and Reproducibility) is a statistical technique used to assess the reliability and consistency of a measurement system. It helps determine how much of the observed variation in measurements is due to the measurement system itself versus actual differences in the items being measured. Repeatability refers to the variation in measurements taken by the same person using the same instrument on the same part multiple times. Reproducibility is the variation in measurements taken by different people using the same instrument on the same part.

A crossed study is the most common type of Gage R&R study, most often used where we are able to instruct each operator to measure each part a fixed number of times. These must be continuous measurements, which means that the result is a number on a scale, as opposed to an attribute gage which gives a Go/No-Go result.

Besides crossed Gage R&R, there are nested GRR and expanded GRR. Nested GR&R is primarily used for destructive testing, where each operator measures different parts. Expanded GR&R builds upon either crossed or nested designs by incorporating additional factors beyond just operators and parts, such as different measurement equipment or environmental conditions.

Crossed Gage R&R requires that operators measure parts in a random order, ensuring the selected parts represent the actual or expected range of process variation. Every operator must evaluate every part, and for optimal results, the study should include 3 to 5 operators, though fewer than 3 may be used if that reflects the actual number of operators using the measurement system. Meanwhile, each operator must measure each part the same number of times to maintain consistency and reliability in the study.

To perform the study, choose Quality > Crossed Gage R&R

.. image:: images/grr1.png
   :align: center

- **Measurement**: The column containing the measurement result. The values must be numerical. 
- **Part**: The column containing the part number. The values will be treated as categorical. 
- **Operators**: When the study has multiple operators, select the column with the operator indicator. The values will be treated as categorical.
- **Algo setting / Method**: There are 3 different algorithm available for the study. The EMP and AIAG methods that align with JMP 17 have small differences. The Xbar/R method is a tranditional approach to perform the study. Their comparison will be discussed.
- **Operator x Part Interaction**: Toggle to include the interaction as a source of variation. Two way ANOVA study can be used to determine whether to include this item, which will be discussed.
- **Plot Y Label**: Set the Y label for the distribution chart plotted. By default it uses the column name of measurement as the Y axis label.


AIAG GRR
--------

AIAG (Automotive Industry Action Group) Gage R&R is a standardized method for assessing measurement system capability in the automotive industry. It is widely used as a standard for GRR outside of the auto industry too. The calculation uses two way ANOVA which is type III sum of squares. The type III method is relatively new. However, the JMP 17 and Minitab 22 are using the method by default for GRR studies. The method here aligns with JMP 17 measurement system analysis > Gage R&R > crossed. The Minitab 22 has it at Gage study > Gage R&R crossed, but it automatically chooses whether to use the interaction factor which will be discussed.

Open the sample data file `gasket.pickle`, select `Measurement` by `Y`, operators and parts. The result is below. 


.. code-block:: none

   ---- GRR AIAG (JMP 17) ----
   Variance Components
   +-----------------+---------+---------------------+
   |      Source     | 6 x SD  |                     |
   +-----------------+---------+---------------------+
   |  Repeatability  |  20.96  | Equipment Variation |
   | Reproducibility |  26.72  | Appraiser Variation |
   |     Operator    |  26.48  |                     |
   |    Op. X Part   |   3.57  |                     |
   |    Gauge R&R    |  33.96  |                     |
   |  Part Variation |  138.24 |    Part Variation   |
   | Total Variation |  142.35 |                     |
   +-----------------+---------+---------------------+
   Gauge R&R / Total Variation = 23.9%
   Number of Distinct Categories = 5
   
   Variance Components of GRR
   +-----------------+--------+---------+---------------+
   |      Source     |  SD    | VarComp | %Contribution |
   +-----------------+--------+---------+---------------+
   |     Ttl GRR     | 5.660  |  32.033 |      5.69     |
   |  Repeatability  | 3.493  |  12.200 |      2.17     |
   | Reproducibility | 4.453  |  19.833 |      3.52     |
   |   Product Var.  | 23.039 | 530.813 |     94.31     |
   +-----------------+--------+---------+---------------+

Use the variance components (VarComp) and %Contribution to assess the variation for each source of measurement error. The sources are as follows:

- Total Gage R&R: The sum of the repeatability and the reproducibility variance components.
- Repeatability: The variability in measurements when the same operator measures the same part multiple times, which is the variation introduced by the equipment.
- Reproducibility: The variability in measurements when different operators measure the same part, which includes the viriation introduced by operators, and the variation that is from the operator and part interaction. An interaction exists when an operator measures different parts differently.
- Product Variance: also known as Part-to-Part variance, it is the variability in measurements due to different parts.

Ideally, very little of the variability should be due to repeatability and reproducibility. Differences between parts (Part-to-Part) should account for most of the variability.

The %Contribution for Total Gage R&R is 5.69% and for Part-to-Part variation is 94.31%. When the %Contribution from part-to-part variation is high, the measurement system can reliably distinguish between parts. The acceptability of a measurement system is determined by the percentage of variance components. If the variance components are less than 1%, the measurement system is considered acceptable. When the variance components fall between 1% and 9%, the system may still be acceptable, but this depends on factors such as the specific application, the cost of the measurement device, the cost of repairs, or other relevant considerations. However, if the variance components exceed 9%, the measurement system is deemed unacceptable and should be improved to ensure accurate and reliable results.

The %Contribution was calculated with the variances which are the squares of the standard deviations. The variances can be added together to the total variances, due to the nature of sums of squares. However, standard deviations don't have the property. There is another way to evaluate the significance of the gage system variation, is the ratio of GRR variation (standard deviation) and the total variation (standard deviation). The ratio is printed below the Variance Component table. 

According to AIAG guidelines, if the measurement system variation is less than 10% of the process variation, then the measurement system is acceptable. A system with variation < 30% is conditionally acceptable. The Total Gage R&R is 23.71% of the study variation. The Total Gage R&R variation might be acceptable depending on the application. Corrective action for improving the measurement system might include training operators or acquiring better gages.

The Number of Distinct Categories (NDC) is a key metric in a Gage R&R study that evaluates a measurement system's ability to differentiate between varying levels of variability in the measured characteristic. It indicates the number of non-overlapping confidence intervals that span the range of product variation, providing insight into the system's resolution and effectiveness.

The interpretation of NDC values is as follows: If the NDC is less than 2, the measurement system lacks the capability to distinguish between parts, indicating poor resolution. An NDC between 2 and 4 suggests a limited ability to detect variability, meaning the system can differentiate parts but with significant constraints. For most applications, an NDC of 5 or greater is considered acceptable, as it demonstrates the measurement system's ability to reliably distinguish between parts and effectively capture variability.

EMP Method
----------

EMP in GRR stands for Evaluating the Measurement Process. It is an alternative approach to analyzing measurement system capability, developed by Dr. Donald Wheeler. EMP calculates variation based on variance, where the sum of all variation components equals 100% of total variation. 

Use the same data from the last session but choose EMP as the method. The result is as below.

.. code-block:: none

   ---- GRR EMP (JMP 17) ----
   Variance Components
   +-----------------+--------+---------+---------------+
   |      Source     | Stdev  | VarComp | %Contribution |
   +-----------------+--------+---------+---------------+
   |     Ttl GRR     | 5.628  |  31.679 |      5.63     |
   |  Repeatability  | 3.493  |  12.200 |      2.17     |
   | Reproducibility | 4.414  |  19.479 |      3.46     |
   |   Product Var.  | 23.039 | 530.813 |     94.31     |
   |   Interaction   | 0.595  |  0.354  |      0.06     |
   | Total Variation | 23.724 | 562.846 |     100.00    |
   +-----------------+--------+---------+---------------+


JMP 17 doesn't include the classification of the EMP methods like Minitab. The output here aligns with JMP. The %Contribution interpretation is similar to the one in AIAG method above. However, Wheeler added a set of classification method for EMP, which may be a subject to add in the future. 

But to compare the results of variance components themselves in AIAG and EMP methods, the difference is how to treat the interaction of operators and parts. In AIAG the interaction is included in the reproducibility together with the operator considerations. It is counted in the total variation but not included in the reproducibility in EMP method. 

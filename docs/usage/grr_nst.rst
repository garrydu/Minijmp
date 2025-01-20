
.. raw:: html

   <style>
      .tight-table td {
             white-space: normal !important;
                       }
                          </style>

Nested Gage R&R
===============

Crossed and nested Gage R&R (Repeatability and Reproducibility) studies are two different approaches to assessing measurement system variation, each suited for specific testing scenarios. Choosing between crossed and nested designs depends on the nature of the measurement process and whether parts can be measured multiple times without alteration.


.. list-table:: Comparison of Crossed and Nested GR&R
   :header-rows: 1
   :widths: 20 40 40
   :class: tight-table

   * - Aspect
     - Crossed GR&R
     - Nested GR&R
   * - Testing Type
     - Non-destructive
     - Destructive
   * - Part Allocation
     - All operators measure all parts
     - Each operator measures unique parts
   * - Interaction Estimation
     - Can estimate part-operator interaction
     - Cannot estimate part-operator interaction
   * - Applicability
     - Parts can be measured multiple times
     - Parts are altered or destroyed during measurement
   * - Assumptions
     - No specific assumptions about part homogeneity
     - Assumes homogeneity within batches of parts
   * - Analysis Method
     - Average and Range or ANOVA
     - Typically requires ANOVA
   * - Part Reuse
     - Parts are reused across operators
     - Parts are not reused
   * - Flexibility
     - More flexible, allows for comprehensive analysis
     - Less flexible, but necessary for certain scenarios

To perform nested GRR choose Quality > Nested Gage R&R

.. image:: images/grr_nst1.png
   :align: center



- **Measurement**: Select the column containing the measurement result. The values must be numerical.
- **Part**: The column containing the part number. The values will be treated as categorical.
- **Operators**: The study requires multiple operators, select the column with the operator indicator. The values will be treated as categorical.
- **Historical Process Std Dev**:


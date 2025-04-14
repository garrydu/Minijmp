Process Capability
==================

Process capability measurement is a statistical method used to evaluate how well a manufacturing process can produce parts within specified limits consistently. The main indices used for this measurement are Cp, Cpk, Pp, and Ppk. The function is to evaluate data without subgrouping, for example, lot, machine, etc.. Use the function of `Cpk with subgroups` for subgrouped data instead.

Choose Quality > Process Capability

.. image:: images/cpk1.png
   :align: center


- **Measurement**: The column containing the measurement result. The values must be numerical and continuous. The caculation assumes the data following normal distribution. Nonnormal distribution evaluation is not available yet.
- **Spec Limits**: To perform the analysis, you must specify a lower (LSL) and upper (USL) specification limit to define your process requirements. Target of the process can also be specified. When leaving the Target value zero, the software will use the mean of LSL and USL as the target. 
- **Show within sigma**: This is a way to evaluate potential (within) capability. Without subgroups, the software will take a moving window of 2 data points to form the pseudo subgroups for the analysis.
- **Plot Settings**:
  - **X Label**: Customize the label of x axis. By default, the software will use the column name of the measurement input.
  - **Show Spec Limits**: Show vertical lines to mark the USL, LSL and Target in the plot. 
  - **Show Legend**: Legend will be only shown when `Show within Sigma` is enabled, by default. Use the selection to override. 

- **Alpha**: Set confidence interval range. For example CI range will be 95% when alpha is 0.05.


The result aligns with JMP 17.


Open the file `CPK_sample.pickle` in the sample data folder. Select `Measurement` with column `Y`. Set the LSL, USL and Target to 17, 23 and 20. The plot and results below will be displayed. 

.. image:: images/cpk2.png
   :align: center

The plot contains the histogram of the data and the normal distribution fit. The histogram bar charts uses the Y axis on the right hand side, which showing the counts of the data poionts falling into each bin. The normal distribution fit curve uses the Y axis on the left hand side, which is the probability density. In the meanwhile the probability density axis is also used by the histogram, it demonstrates the integrated probability of each bin.


.. code:: none

   ---- Process Capabilities ----
   LSL = 17.000
   USL = 23.000
   Target = 20.000
   mean = 20.397
   Overall Sigma = 1.475
   N = 32
   N Subgroups = 0
   
   Overall (AKA Ppk in JMP)
   +-------+----------+--------------+--------------+
   | Index | Estimate | Lower 95.00% | Upper 95.00% |
   +-------+----------+--------------+--------------+
   |  Cpk  |  0.588   |    0.402     |    0.775     |
   |  Cpl  |  0.768   |    0.543     |    0.988     |
   |  Cpu  |  0.588   |    0.400     |    0.772     |
   |   Cp  |  0.678   |    0.510     |    0.846     |
   |  Cpm  |  0.655   |              |              |
   +-------+----------+--------------+--------------+
   
   Nonconformance (Observation and Expected)
   +-----------+-----------+-------------------+
   |  Portion  | Observed% | Expected Overall% |
   +-----------+-----------+-------------------+
   | Below LSL |    3.12   |        1.06       |
   | Above USL |    3.12   |        3.88       |
   | Total Out |    6.25   |        4.94       |
   +-----------+-----------+-------------------+


The first part of the numerical prints includes general information of the study. The `Overall Sigma` is the standard deviation of the sample data. `N subgroups` is zero here because the study didn't contain subgroups of data.

**Cp (Process Capability)**

- Measures the **potential capability** of a process to produce output within specification limits, assuming the process is centered
- Formula::
  
    Cp = \frac{USL - LSL}{6\sigma}

  where:
  - USL = Upper Specification Limit
  - LSL = Lower Specification Limit
  - σ = process standard deviation

**Cpk (Process Capability Index)**
- Measures **actual capability** by considering both process variation and centering
- Formula::
  
    Cpk = \min\left(\frac{USL - \mu}{3\sigma}, \frac{\mu - LSL}{3\sigma}\right)

  where μ = process mean


**Cpu (Upper Capability Index)**
- Evaluates **upper specification limit** performance::
  
    Cpu = \frac{USL - \mu}{3\sigma}
- Focuses on risk of exceeding upper tolerance

**Cpl (Lower Capability Index)**
- Evaluates **lower specification limit** performance::
  
    Cpl = \frac{\mu - LSL}{3\sigma}
- Focuses on risk of falling below lower tolerance

**Cpm (Process Capability Index for Target)**
- Incorporates **deviation from target value** (T)::
  
    Cpm = \frac{USL - LSL}{6\sqrt{\sigma^2 + (\mu - T)^2}}
- Penalizes processes where mean (μ) deviates from target (T)





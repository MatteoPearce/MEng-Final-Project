This project is a study into the feasibility of biosensors comprised of thin magnetic films acting
as reservoirs in the context of Reservoir Computing, a novel machine learning technique that
embeds neural computation in the natural properties of a physical substrate. A single output
layer of neurons is trained to read changes in one or more fundamental states of the reservoir,
and extrapolate the causal input to the physical medium. Thin-films are grown epitaxially and
structures can be assembled with nanoscale dimensions, featuring clear magnetic properties. A
vast number of biological mechanisms take advantage of ionised elements and their movement.
These particles generate fluctuating magnetic fields and it is hoped that these are of sufficient
intensity to measurably change the polarisation of a magnetic nanostructure, such that the
output layer of neurons can learn to infer patterns that may equate to events in the associated
biology. This project aims to assess feasibility in each of the umbrella concepts that govern this
implementation, such that the degree of remuneration from continuing this line of exploration is
unequivocal. Due to the inherent difficulties and extreme costs associated with manufacturing
one-off nanostructures, all physical elements will be simulated in software, with the University of
York’s in-house atomistic simulator: Vampire. Furthermore, in light of the strengths, scalability
and flexibility of high level programming languages, the neuron output layer will be emulated
in Python. Developing the moving parts of the project in software increases portability and
format compatibility between shared datasets.

Random search exploration in Python of system parameters for thin ferromagnetic films (Co, Fe, Ni), simulated with the Vampire atomistic simulator and used as reservoirs according to the Reservoir Computing machine learning paradigm. Properties such as Gilbert magnetic damping and parameters such as input scaling, film dimensions and readout discretisation are trialled in different combinations to assess the effects on NRMSE in predicting the NARMA10 algorithm, injected into the film as a z-component magnetic field intensity. An appraisal of the compatibility of this technology with biomagnetic signals as a feasibility study into the application of such films for in-situ biosensors. Exploration of novel implementations such as body-temperature test conditions, equal input scaling and uniform signal injection are trialled as cornerstone concepts for the suggested use-case, with the latter constituting a significant roadblock. Film dimensions emerge as a clear strategy for mitigating errors, and pico-Tesla signals display good compatibility with the ferromagnetic mediums. 

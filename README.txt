1. Names: Michael Ho and Romi Phadte
2. What challenges did you face while implementing your router?
We faced problems when links were destroyed, because when the link's weight changed to infinite, the entity would turn to a different direction and use that link's distance to a destination, even though that destination also needed to traverse the same link. 
We also had trouble with our routers sending infinite loops of data between each other when we split our network into two separate networks of routers. Error handling of broken links did not perform well.


3. Name a feature NOT implemented in this specification that would improve your router.
The use of a hierarchical structure of addresses, where each entity's address included the path to reach it, would help our router system scale by allowing routing based on longest-prefix matching of addresses. Our current routers must maintain a routing table with at least every entity it can reach in order to know how to route to the specified destination. A hierarchical addressing scheme would allow our routers to send packets to the router who is in charge of the end system, without having to know every single host that router has under its umbrella. 

4. Specify if your code can handle link weights or do incremental updates. If you have implemented any of them, describe what additional considerations need to be taken into.
Our code can handle link weights and do incremental updates.
For link weights, we simply specify a different weight. We now must take into consideration when a direct link is not the fastest route to a destination. We also had to take into consideration when a link weight possibly approached infinity.
For incremental updates, we needed to create a list of changes made that had to be cleared and kept up to date. We had to make sure updates were being propagated properly across the network.

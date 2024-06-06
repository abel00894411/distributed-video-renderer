This project is a distributed video renderer that will transform a set of images into a MP4 video. It's composed of two Python scripts, one for a server that will get rendered video segments by following the ambassador pattern, and the other for a client or node, that will do the CPU-intensive work of transforming the images into a video file.

## The ambassador

The ambasador (server.py) is a server program that will establish connection with nodes (clients) to assign them work and receive the resulting data that will then be merged into a single file.

The excecution of the program starts by dividing the work in sets of a hundred images, that will be stored in a list and assigned to nodes as they become availaible for working. The result received from the node will then be processed by a circuit breaker, that will take a course of action depending on the type of response. The received video segments will then be stored locally, and when all segments have been processed by the nodes, the ambassador will merge them into a single video.

## The node

The node (nodo.py) is a client program that will establish connection with the ambassador server, and will get from it sets of paths of images that it will process into a video that will be sent back to the ambassador. After sending the resulting video data, the node will receive a new set to work on, until all of the sets are processed. The videos produced by the node are rendered at 20fps.


![saving-videos](https://github.com/abel00894411/distributed-video-renderer/assets/133552182/8678e690-b030-4d99-b9bf-e06ebe856e12)
![rendering-set](https://github.com/abel00894411/distributed-video-renderer/assets/133552182/6fbd4b2f-53c5-493d-a3a7-21f048ae7582)

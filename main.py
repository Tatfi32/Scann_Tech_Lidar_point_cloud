# ! in package.PcapParser.seq_processing() front hemisphere is selected only. Beware!
import package
import pandas as pd
import pickle
# Do not remove this line its required by scatter3D indirectly
from mpl_toolkits.mplot3d import axes3d, Axes3D
from pathlib import Path

"""
get list of sequences path to be loop thought in one series (one relief) group
each path processed with constant scripts:
                                            video_parser(path to the video folder)
                                            read_pcap(path to the pcap folder)
                                            camera(path to the frames folder)
                        dynamic scripts: 
                                            projection(camera_position =  [bias value, 0 ,0] position)
                                            
project all points_cloud from  projection script to one image                                     
                    visualizator.plot_picture
               
"""
sequence_path = Path.cwd() / 'data'
result = pd.DataFrame()
sequence_paths = [x for x in sequence_path.iterdir() if x.is_dir()]

camera_seq_position = [-0.75, 0, 0]

for seq_path in sequence_paths:
    #Video Parsing
    parser = package.Parser(path=seq_path)
    parser.read()

    # Reading pcap binaries
    pcap_file_path = [x for x in seq_path.glob('*.pcap*') if x.is_file()][0]
    pcap = package.PcapReader(pcap_file_path)
    lidar_data = pcap.get_pcap_data()

    # Projecting on camera

    # Selecting pixels corresponding to the board
    constraints = {'x_min': -708, 'x_max': 292, 'y_min': -410, 'y_max': 190 }
    camera = package.Camera(constraints=constraints)

    projector = package.Projector(camera_position = camera_seq_position)
    camera_seq_position[0] = camera_seq_position[0] + 0.009

    data = projector.project(lidar_data)
    data = camera.project(data)

    # Additional depth constraint to remove falling out points
    data = data[data['Z'] < 1.3]
    data = data[data['Z'] > 1 ]
    print(result.shape)
    result = pd.concat([result, data], ignore_index=True, sort=False)

# Visualization without picture (point cloud)
visualizator = package.Visualizator(df=result)
visualizator.plot_points(output_path=seq_path)

# Visualization with picture (!!!all point goes to the same frame,because camera position was static)
images_file_path = [x for x in (seq_path/'frames').glob('*.bmp*') if x.is_file()][0]
visualizator.plot_picture(str(images_file_path), output_path=seq_path)











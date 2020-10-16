# ! in package.PcapParser.seq_processing() front hemisphere is selected only. Beware!
import package
import pandas as pd
# Do not remove this line its required by scatter3D indirectly
from mpl_toolkits.mplot3d import axes3d, Axes3D
from pathlib import Path

"""
1- get list of sequences path to be loop thought in one series (one relief) group
2 - each path processed with constant scripts:
                                            video_parser(path to the video folder)
                                            read_pcap(path to the pcap folder)
                                            camera(path to the frames folder)
                        dynamic scripts: 
                                            projection(camera_position =  [bias value, 0 ,0] position)

3 - project all points_cloud from  projection script to one image                                     
4 - save one created image with visualizator.plot_picture

"""
# "data" folder contain from 6 to 8 sub-folders with data from one static flat relief
# each sub_folder contain information about one movement across vertical camera axes (sequence)
# each sub_folder contain *pcap, *avi and calib data files
sequence_path = Path.cwd() / '1'
sequence_paths = [x for x in sequence_path.iterdir() if x.is_dir()]
camera_seq_position = [-0.75, 0, 0]

# create empty DataFrame to accumulate lidar points sequences from each sub_folder
result = pd.DataFrame()

for index, seq_path in enumerate(sequence_paths):
    # Video Parsing
    parser = package.Parser(path=seq_path)
    parser.read()

    # Reading pcap binaries
    # take just first *pcap file because all *pcap folder files from the same relief
    pcap_file_path = [x for x in seq_path.glob('*.pcap*') if x.is_file()][0]
    pcap = package.PcapReader(pcap_file_path)
    lidar_data = pcap.get_pcap_data()

    # Plot points cloud for one sequence before projection
    visualizator = package.Visualizator(output_path=seq_path, df=lidar_data)
    visualizator.plot_scatter_one_seq()

    # Projecting on camera

    # Selecting pixels corresponding to the board
    constraints = {'x_min': -708, 'x_max': 292, 'y_min': -410, 'y_max': 190}
    camera = package.Camera(constraints=constraints)

    projector = package.Projector(camera_position=camera_seq_position)
    camera_seq_position[0] = camera_seq_position[0] + 0.05

    data = projector.project(lidar_data)
    data = camera.project(data)

    # Additional depth constraint to remove falling out points
    data = data[data['Z'] < 1.3]
    data = data[data['Z'] > 1]
    data['seq_number'] = index

    result = pd.concat([result, data], ignore_index=True, sort=False)

# Plot point cloud lidar series from several lidar position on one figure (without picture)
# Different color represent diferent lidar position in each sequence
visualizator = package.Visualizator(sequence_path, df=result)
visualizator.plot_seq_points(df=result)

# Visualization with picture
# !!!all point goes to the same frame,because camera position was static
images_file_path = [x for x in (seq_path / 'frames').glob('*.bmp*') if x.is_file()][0]
visualizator.plot_picture(str(images_file_path))











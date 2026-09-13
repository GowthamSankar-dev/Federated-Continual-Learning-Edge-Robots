import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from pathlib import Path


class CameraCapture(Node):

    def __init__(self):
        super().__init__('camera_capture')

        self.bridge = CvBridge()

        # Folder where captured images will be stored
        self.output_dir = Path.home() / 'fcl-edge-robots' / 'data'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.image_count = 0

        # Subscribe to TurtleBot4 camera
        self.subscription = self.create_subscription(
            Image,
            '/oakd/rgb/preview/image_raw',
            self.image_callback,
            10
        )

        self.get_logger().info('Camera capture node started.')
        self.get_logger().info(
            f'Saving images to: {self.output_dir}'
        )

    def image_callback(self, msg):

        try:
            # Convert ROS Image → OpenCV image
            image = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

            self.image_count += 1

            filename = (
                self.output_dir /
                f'camera_{self.image_count:04d}.jpg'
            )

            # Save image
            cv2.imwrite(str(filename), image)

            self.get_logger().info(
                f'Saved {filename.name} '
                f'({image.shape[1]}x{image.shape[0]})'
            )

        except Exception as e:
            self.get_logger().error(
                f'Failed to process image: {e}'
            )


def main(args=None):

    rclpy.init(args=args)

    node = CameraCapture()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

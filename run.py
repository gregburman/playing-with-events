import tkinter
import time
import random

WINDOW_SIZE = 640
PIXEL_SIZE = 20
RESOLUTION = 32
FRAMERATE = 15
GRID_OUTLINE = True
LEAST_EVENTS = 20
MOST_EVENTS = 30
TIMESTEPS = 100

class Event():

	def __init__(self, x, y, p, t):
		self.x = x
		self.y = y
		self.p = p
		self.t = t

	def __repr__(self):
		return str((self.x, self.y, self.p, self.t))


def generate_noise_event_stream(timesteps):
	all_events = []
	for t in range(timesteps):
		num_events = random.randint(LEAST_EVENTS, MOST_EVENTS)
		events = []
		for i in range(num_events):
			x = random.randint(0, RESOLUTION - 1)
			y = random.randint(0, RESOLUTION - 1)
			p = random.choice([-1, 1])
			event = Event(x, y, p, t)
			events.append(event)
		all_events.append(events)
	return all_events

def generate_sony_event_stream(timesteps):
	all_events = []
	positions = [(i, 8) for i in range(8, 24)] + \
				[(8, i) for i in range(8, 16)] + \
				[(i, 16) for i in range(8, 24)] + \
				[(23, i) for i in range(16, 24)] + \
				[(i, 24) for i in range(8, 24)]

	for t in range(timesteps):
		events = []
		for position in positions:
			event = Event(position[0], position[1], 1, t)
			events.append(event)
		all_events.append(events)
	return all_events

def combine_streams(stream_a, stream_b):
	all_events = []
	for events_a, events_b in zip(stream_a, stream_b):
		all_events.append(events_a + events_b)
	return all_events



def clear_pixels(canvas, pixels):
	for i in range(RESOLUTION):
		for j in range(RESOLUTION):
			canvas.itemconfig(pixels[i][j], fill='black')


if __name__ == '__main__':
	# create window
	window = tkinter.Tk()
	window.title("Playing With Events")
	window.geometry('{}x{}'.format(WINDOW_SIZE, WINDOW_SIZE))

	# create canvas
	canvas = tkinter.Canvas(window)
	canvas.configure(bg="black")
	canvas.pack(fill="both", expand=True)

	# create pixels
	pixels = [[None]*RESOLUTION for i in range(RESOLUTION)]
	outline = 'white' if GRID_OUTLINE else None
	for x in range(RESOLUTION):
		for y in range(RESOLUTION):
			pixels[y][x] = canvas.create_rectangle(x*PIXEL_SIZE, y*PIXEL_SIZE, x*PIXEL_SIZE+PIXEL_SIZE, y*PIXEL_SIZE+PIXEL_SIZE, fill='black', outline=outline)

	# window.update()
	# input('press enter when ready to start')

	# here we're streaming in events
	sony_event_stream = generate_sony_event_stream(TIMESTEPS)
	noise_event_stream = generate_noise_event_stream(TIMESTEPS)
	event_stream = combine_streams(sony_event_stream, noise_event_stream)
	for i, timestep in enumerate(event_stream):
		clear_pixels(canvas, pixels)
		print('timestep:', i)
		for event in timestep:
			color = 'green' if event.p == 1 else 'red'
			canvas.itemconfig(pixels[event.y][event.x], fill=color)
		window.update()
		time.sleep(1/FRAMERATE)
	window.show()

	events = generate_events()
	print('hello:', events[0][0])

import argparse
import itertools
import numpy as np
import time
import tkinter
import random

# user-friendly parameters to play with

# for reasons explained below, these parameters should not be changed, as doing so
# will likely break the display.
WINDOW_SIZE = 1000
PIXEL_SIZE = 15
RESOLUTION = 32

# class used to represent events. At first look, events could be easily represented
# by simple data structures such as tuples or lists, however encapsulating them in a
# class is useful for adding additional attributes (here is_valid), or functions, if needed.
class Event():

	def __init__(self, x, y, p, t):
		self.x = x
		self.y = y
		self.p = p
		self.t = t
		self.is_valid = True

	def __repr__(self):
		return str((self.x, self.y, self.p, self.t))

# generate random noise, with amount set by LEAST_EVENTS and MOST_EVENTS.
def generate_noise_event_stream(timesteps, noise_bounds):

	# generate full set of x, y pixel grid coordinates to sample the noisy events from.
	Y = [i for i in range(RESOLUTION)]
	X = [i for i in range(RESOLUTION)]
	coords = []
	for i, j in itertools.product(Y, X):
		coords.append((i, j))

	# generate a random number events between bounds at each timestep. Note that event
	# is also randomly chosen.
	all_events = []
	for t in range(timesteps):
		num_events = random.randint(noise_bounds[0], noise_bounds[1])
		random_sample = random.sample(coords, k=num_events)
		events = []
		for i in range(num_events):
			x = random_sample[i][1]
			y = random_sample[i][0]
			p = random.choice([-1, 1])
			event = Event(x, y, p, t)
			events.append(event)
		all_events.append(events)
	return all_events

# generate hardcoded S-shape - this is the reason that RESOLUTION should be set to 32,
# as I haven't implemented the calculations to dynamically adjust the size of the S-shape
def generate_sony_event_stream(timesteps):
	all_events = []
	#define all event positions
	positions = [(i, 8) for i in range(8, 24)] + \
				[(8, i) for i in range(8, 16)] + \
				[(i, 16) for i in range(8, 24)] + \
				[(23, i) for i in range(16, 24)] + \
				[(i, 24) for i in range(8, 24)]

	# generate corresponding events
	for t in range(timesteps):
		events = []
		for position in positions:
			event = Event(position[0], position[1], 1, t)
			events.append(event)
		all_events.append(events)
	return all_events

# note that events with the same timestamp and x, y coordinates will overlap - this is
# is actually a BUG, however it seems unclear how to approach it.
def combine_streams(stream_a, stream_b):
	all_events = []
	for events_a, events_b in zip(stream_a, stream_b):
		all_events.append(events_a + events_b)
	return all_events

# this function filters events which do not have neighbours in the current timestep or
# appear in the previous timestep or have neighbours then either. Events appearing in the
# previous timestep are stored in a buffer array.
def filter_noise_events(event_stream):

	def create_buffer(event_stream, t):
		buff = np.zeros([RESOLUTION, RESOLUTION], dtype=np.int8)
		for event in event_stream[t]:
			buff[event.y][event.x] = event.p
		return buff

	# start at the 2nd timestep as we don't have any basis to filter events in the first
	# timestep.
	for t in range(1, len(event_stream)):
		# populate the buffers
		buffer_prev = create_buffer(event_stream, t-1)
		buffer_curr = create_buffer(event_stream, t)
		num_events = len(event_stream[t])
		for e, event in enumerate(event_stream[t]):
			found_event = False
			# check neighbourhood (again, am aware this is not very efficient - 4 nested loops):
			for i in range(-1, 2):
				for j in range(-1, 2):
					if event.y + i >= 0 and event.y + i < RESOLUTION and event.x + j >= 0 and event.x + j < RESOLUTION:
						if buffer_prev[event.y + i][event.x + j] != 0 or \
							(buffer_curr[event.y + i][event.x + j] != 0 and (i != 0 and j != 0)): # found event, do not remove
							found_event = True
							break # small efficiency gain
				if found_event:
					break # small efficiency gain

			if not found_event:
				# invalid events will be removed in the output stream
				event_stream[t][e].is_valid = False

	# I tried removing events from the stream as I was going through it, but found this
	# messy, so I just decided to use the is_valid property to mark events which should
	# not be included in the output stream.
	output_event_stream = []
	for events in event_stream:
		events_out = []
		for event in events:
			if event.is_valid:
				events_out.append(event)
		output_event_stream.append(events_out)
	return output_event_stream

# function to draw the 4 pixel grids which the streams will be displayed on
# (this funciton is only run once at the start of the programme, so efficiency isn't super
# important here)
def create_pixel_grids(canvas, hide_grid_outline):
	outline = 'white' if not hide_grid_outline else None
	pixel_grids = [[[None]*RESOLUTION for m in range(RESOLUTION)] for n in range(4)]

	# left the offsets as hardcoded for now
	offsets = [[10, 10], [WINDOW_SIZE/2 + 10, 10], [10, WINDOW_SIZE/2 + 10], \
		[WINDOW_SIZE/2 + 10, WINDOW_SIZE/2 + 10]]

	grid_length = RESOLUTION * PIXEL_SIZE
	for pixel_grid, offset in zip(pixel_grids, offsets):
		
		
		# draw pixels
		for x in range(RESOLUTION):
			for y in range(RESOLUTION):
				pixel_grid[y][x] = canvas.create_rectangle(
					x * PIXEL_SIZE + offset[0],
					y * PIXEL_SIZE + offset[1],
					x * PIXEL_SIZE+PIXEL_SIZE + offset[0],
					y * PIXEL_SIZE+PIXEL_SIZE + offset[1],
					fill='black', outline=outline)

		# draw grid area outlines:
		canvas.create_rectangle(
			offset[0],
			offset[1],
			offset[0] + grid_length,
			offset[1] + grid_length,
			fill='', outline='white')
	return pixel_grids

# function to clear the pixel grids at the start of each timestep
# (I'm aware that the complexity is O(N^2) and that there's likely a more efficient way
# of doing this)
def clear_grid(canvas, grid, hide_grid_outline):
	for i in range(RESOLUTION):
		for j in range(RESOLUTION):
			if hide_grid_outline:
				canvas.itemconfig(grid[i][j], fill='black', outline='black')
			else:
				canvas.itemconfig(grid[i][j], fill='black')
def run(args):

	# create window
	window = tkinter.Tk()
	window.title("Playing With Events")
	window.geometry('{}x{}'.format(WINDOW_SIZE, WINDOW_SIZE))

	# create canvas
	canvas = tkinter.Canvas(window)
	canvas.configure(bg="black")
	canvas.pack(fill="both", expand=True)

	# create pixel grids
	pixel_grids = create_pixel_grids(canvas, args.hide_grid_outline)

	# generate, aggregate and filter event streams
	t0 = time.time()
	sony_event_stream = generate_sony_event_stream(args.timesteps)
	noise_event_stream = generate_noise_event_stream(args.timesteps, args.noise_bounds)
	combined_event_stream = combine_streams(sony_event_stream, noise_event_stream)
	filtered_event_stream = filter_noise_events(combined_event_stream)
	print("time to generate all event streams: {}s".format(round(time.time() - t0, 3)))

	window.update() # to display the pixel grids before running the actual programme
	input('press enter when ready to start')

	# order of streams in lists determines where they appear in the display
	streams = [noise_event_stream, sony_event_stream, combined_event_stream, filtered_event_stream]

	for timestep, event_streams in enumerate(zip(*streams)):
		t0 = time.time()
		for i, event_stream in enumerate(event_streams):
			clear_grid(canvas, pixel_grids[i], args.hide_grid_outline)
			for event in event_stream:
				color = 'green' if event.p == 1 else 'red'
				if args.hide_grid_outline:
					canvas.itemconfig(pixel_grids[i][event.y][event.x], fill=color, outline=color)
				else:
					canvas.itemconfig(pixel_grids[i][event.y][event.x], fill=color)
		num_unfiltered_events = len(event_streams[2])
		num_filtered_events = len(event_streams[3]) 
		window.update()
		print('timestep: {} ({}s); filtered / unfiltered: {}/{}'.format(timestep, round(time.time() - t0, 3), num_filtered_events, num_unfiltered_events))
		time.sleep(1/args.framerate)


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--timesteps', required=True, type=int)
	parser.add_argument('--framerate', required=False, type=int, default=30)
	parser.add_argument('--noise-bounds', required=False, type=int, nargs='+', default=(2, 10))
	parser.add_argument('--hide-grid-outline', required=False, action="store_true")
	args = parser.parse_args()

	# call the main function to run the programme
	run(args)

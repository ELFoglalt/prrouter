from timeit import default_timer as dtimer
exec_start = dtimer()

import argparse
import os
import yaml
import json
from math import ceil
from PIL import Image, ImageDraw, ImageFont, ImageColor
from sys import stdout
import functools
import sys

version = '1.0'

def add_message(message, overwrite, reason='', indent=0, first=False):
    id = indent * '\t'
    if reason == '':
        message = ('\r' if overwrite else '') + '[    ] ' + id + message
    elif reason == 'success':
        message = ('\r' if overwrite else '') + '\033[92m[DONE]\033[0m ' + id + message
    elif reason == 'notice':
        message = ('\r' if overwrite else '') + '\033[94m[INFO]\033[0m ' + id + message
    elif reason == 'fail':
        message = ('\r' if overwrite else '') + '\033[91m[FAIL]\033[0m ' + id + message
    elif reason == 'header':
        message = ('\r' if overwrite else '') + '\033[95m------ ' + id + message + '\033[0m'
    else:
        raise Exception('Git gud')
    stdout.write(('' if overwrite or first else '\n') + message)
    stdout.flush()


def getAbsoluteResourcePath(relativePath):
    #TODO: fix single file build
    #try:
    #    # PyInstaller stores data files in a tmp folder refered to as _MEIPASS
    #    basePath = sys._MEIPASS
    #except Exception:
    #    basePath = ''
    #
    #path = os.path.join(basePath, relativePath)
    #
    # If the path still doesn't exist, this function won't help you
    #if not os.path.exists(path):
    #    return None
    return relativePath


def draw_circle_centered(image, position, radius, thickness=2, color='white', antialias=6):
    l, t = [val - radius for val in position]
    r, b = [val + radius for val in position]
    draw_ellipse(image, [l, t, r, b], thickness=thickness, color=color, antialias=antialias)

def fill_circle_centered(image, position, radius, color='white', antialias=6):
    l, t = [val - radius for val in position]
    r, b = [val + radius for val in position]
    fill_ellipse(image, [l, t, r, b], color=color, antialias=antialias)

def fill_ellipse(image, bounds, color='white', antialias=6):
    a = ImageColor.getcolor(color, 'RGBA')[-1]
    l, t, r, b = bounds
    w = r - l
    h = b - t
    if w == 0 or h == 0: return
    wg = w > h
    ar = (w if wg else h) > (h if wg else w)
    hmmarg = ceil(antialias * (ar if wg else 1))
    vmmarg = ceil(antialias * (1 if wg else ar))
    himarg = ceil(ar if wg else 1)
    vimarg = ceil(1 if wg else ar)
    mw = w * antialias + hmmarg*2
    mh = h * antialias + vmmarg*2
    ml = hmmarg
    mt = vmmarg
    mr = mw - hmmarg
    mb = mh - vmmarg
    il = l - himarg
    it = t - vimarg

    mask = Image.new(
        size=[mw, mh],
        mode='L', color='black')
    draw = ImageDraw.Draw(mask)

    draw.ellipse([ml, mt, mr, mb], fill=a) #ml, mt, mr, mb?

    # downsample the mask using PIL.Image.LANCZOS
    # (a high-quality downsampling filter).
    mask = mask.resize((w + himarg*2, h + vimarg*2), Image.BILINEAR)
    # paste outline color to input image through the mask
    image.paste(color, box=[il, it], mask=mask)

def draw_ellipse(image, bounds, thickness=2, color='white', antialias=6):
    a = ImageColor.getcolor(color, 'RGBA')[-1]
    l, t, r, b = bounds
    w = r - l
    h = b - t
    if w == 0 or h == 0: return
    wg = w > h
    ar = (w if wg else h) > (h if wg else w)
    mthickness = thickness * antialias
    hmmarg = ceil(antialias * (ar if wg else 1))
    vmmarg = ceil(antialias * (1 if wg else ar))
    himarg = ceil(ar if wg else 1)
    vimarg = ceil(1 if wg else ar)
    mw = w * antialias + hmmarg*2
    mh = h * antialias + vmmarg*2
    ml = hmmarg
    mt = vmmarg
    mr = mw - hmmarg
    mb = mh - vmmarg
    il = l - himarg
    it = t - vimarg

    mask = Image.new(
        size=[mw, mh],
        mode='L', color='black')
    draw = ImageDraw.Draw(mask)

    # draw outer shape in white (color) and inner shape in black (transparent)
    for offset, fill in (0, a), (mthickness, 'black'):
        left, top = [(value + offset) for value in [ml, mt]]
        right, bottom = [(value - offset) for value in [mr, mb]]
        draw.ellipse([left, top, right, bottom], fill=fill)

    mask = mask.resize((w+himarg*2, h+vimarg*2), Image.BILINEAR)
    # paste outline color to input image through the mask
    image.paste(color, box=[il, it], mask=mask)

def draw_line(image, points, thickness=1, color='white', antialias=6):
    a = ImageColor.getcolor(color, 'RGBA')[-1]
    x1, y1, x2, y2 = points
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
    l, r = x1, x2
    t = min(y1, y2)
    b = max(y1, y2)
    w = r - l
    h = b - t
    if w == h == 0: return
    elif w == 0:
        wg, ar = False, 1
    elif h == 0:
        wg, ar = True, 1
    else:
        wg = w > h
        ar = (w if wg else h) / (h if wg else w)
    mthickness = thickness * antialias
    hmmarg = round(0.7 * mthickness * (ar if wg else 1))
    vmmarg = round(0.7 * mthickness * (1 if wg else ar))
    himarg = round(0.7 * thickness  * (ar if wg else 1))
    vimarg = round(0.7 * thickness  * (1 if wg else ar))
    mw = w * antialias + hmmarg*2
    mh = h * antialias + vmmarg*2
    ml = hmmarg
    mt = vmmarg
    mr = mw - hmmarg
    mb = mh - vmmarg
    il = l - himarg
    it = t - vimarg

    mask = Image.new(
        size=[mw, mh],
        mode='L', color='black')
    draw = ImageDraw.Draw(mask)

    draw.line([ml, mt, mr, mb] if (y1 < y2) else [ml, mb, mr, mt], fill=a, width=thickness * antialias)

    mask = mask.resize((w+himarg*2, h+vimarg*2), Image.BILINEAR)
    image.paste(color, box=[il, it], mask=mask)

def draw_text(image, position, text, font=None, typeface=None, fontsize=None, color='white', antialias=4,
              anchor=('l', 'b')):
    if not font:
        if not (typeface and font): raise ValueError("Must specify either font, or typeface and fontsize")
        font = ImageFont.truetype(typeface, fontsize * antialias)
    w, h = font.getsize(text)
    if w == 0 or h == 0: return
    w = round(w/float(antialias))
    h = round(h/float(antialias))
    hanchor, vanchor = anchor
    if hanchor == 'l':
        l = position[0]
        r = l + w
    elif hanchor == 'r':
        r = position[0]
        l = r - w
    elif hanchor == 'm' or hanchor == 'c':
        l = position[0] - ceil(w / 2)
        r = position[0] + ceil(w / 2)
    else: raise ValueError('Horizontal anchor must be exactly one of \'l\', \'r\', or \'m\'/\'c\'')
    if vanchor == 't':
        t = position[1]
        b = t + h
    elif vanchor == 'b':
        b = position[1]
        t = b - h
    elif vanchor == 'm' or vanchor == 'c':
        t = position[1] - ceil(h / 2)
        b = position[1] + ceil(h / 2)
    else: raise ValueError('Vertical anchor must be exactly one of \'t\', \'b\', or \'m\/\'c\'')

    a = ImageColor.getcolor(color, 'RGBA')[-1]
    w = r - l
    h = b - t
    wg = w > h
    ar = (w if wg else h) > (h if wg else w)
    hmmarg = ceil(antialias * (ar if wg else 1))
    vmmarg = ceil(antialias * (1 if wg else ar))
    himarg = ceil(ar if wg else 1)
    vimarg = ceil(1 if wg else ar)
    mw = w * antialias + hmmarg*2
    mh = h * antialias + vmmarg*2
    ml = hmmarg
    mt = vmmarg
    il = l - himarg
    it = t - vimarg

    mask = Image.new(
        size=[mw, mh],
        mode='L', color='black')

    draw = ImageDraw.Draw(mask)
    draw.text([ml, mt], text, fill=a, font=font)

    mask = mask.resize([w + himarg*2, h + vimarg*2], Image.LANCZOS)
    image.paste(color, box=[il, it], mask=mask)





fonts_dir  = 'fonts'
font_ext        = '.ttf'
font_default = 'OpenSans-Light'
map_image_ext    = '.jpg'
overlay_image_ext = '.png'
maps_dir    = 'maps'
images_dir  = os.path.join(maps_dir, 'map_img')
jsons_dir   = os.path.join(maps_dir, 'map_json')
colormaps_file = 'colors.yaml'
colormaps_int_file = 'colors.base.yaml'
overlays_dir = 'overlays'
overlays_file = 'overlays.yaml'
overlays_int_file = 'overlays.base.yaml'
temp_dir    = 'temp'
output_dir  = 'output'
output_ext  = '.png'
output_format = "PNG"
export_cntr = 0

@functools.lru_cache(maxsize=64)
def get_scaled_font(fontname, fontsize, antialias):
    return ImageFont.truetype(os.path.join(fonts_dir, fontname + font_ext), fontsize*antialias)

all_gamemodes_lookup = {
    'AAS_INF': "gpm_cq_16",
    'AAS_ALT': "gpm_cq_32",
    'AAS_STD': "gpm_cq_64",
    'AAS_LRG': "gpm_cq_128",
    'SKIRMISH_INF': "gpm_skirmish_16",
    'SKIRMISH_ALT': "gpm_skirmish_36",
    'SKIRMISH_STD': "gpm_skirmish_64",
    'SKIRMISH_LRG': "gpm_skirmish_128",
    'COOP_INF': "gpm_coop_16",
    'COOP_ALT': "gpm_coop_32",
    'COOP_STD': "gpm_coop_64",
    'COOP_LRG': "gpm_coop_128",
}
all_gamemodes_lookup_inv = {v: k for k, v in all_gamemodes_lookup.items()}

# Reading maps
with open(getAbsoluteResourcePath(os.path.join(jsons_dir, 'maplist.json'))) as maplist:
    map_infos = json.load(maplist)

all_map_names = []
for map_info in map_infos:
    all_map_names.append(map_info['code'])

class OverlayCache:
    def __init__(self, mask, cmap, go, out_size):
        self._mask = mask
        self.output_size = out_size
        self.colormap = cmap
        self.opacity = go
        self._grid_mask_lookup = {}
        self._dim_lookup = {}
        self._base_with_dim_lookup = {}
        self._overlay_rgb_lookup = {}
        self.output_size = output_size

    def get_grid_mask(self, size):
        if self.opacity:
            if size not in self._grid_mask_lookup:
                p = os.path.join(overlays_dir, str(size) + overlay_image_ext)
                scale_image = Image.open(getAbsoluteResourcePath(p))
                a = scale_image.split()[-1]
                a = a.resize((self.output_size, self.output_size), resample=Image.BILINEAR if (scale_image.size[0] > self.output_size) else Image.CUBIC)
                a = a.point(lambda i: i * self.opacity)
                a.paste(self._mask, mask=self._mask)
                self._grid_mask_lookup[size] = a
            return self._grid_mask_lookup[size].copy()
        else:
            return self._mask.copy() if self._mask else False

    def get_overlay_rgb(self, n, size):
        if not self._mask: return False
        n %= len(self.colormap['overlays'])
        if (n, size) not in self._overlay_rgb_lookup:
            mask = self.get_grid_mask(size)
            r, g, b, a = Image.new('RGBA', (self.output_size, self.output_size), self.colormap['overlays'][n]).split()
            mask.paste(a, mask=mask)
            self._overlay_rgb_lookup[(n, size)] = Image.merge('RGBA', (r, g, b, mask))
        return self._overlay_rgb_lookup[(n, size)].copy()

    def get_dim(self, n):
        n %= len(self.colormap['dims'])
        if n not in self._dim_lookup:
            img = Image.new('RGBA', (self.output_size, self.output_size), self.colormap['dims'][n])
            self._dim_lookup[n] = img
        return self._dim_lookup[n].copy()

    def get_composite_overlay(self, n, size):
        if (n, size) not in self._base_with_dim_lookup:
            base = self.get_overlay_rgb(n, size)
            dim = self.get_dim(n)
            if base:
                dim.paste(base, mask=base)
            self._base_with_dim_lookup[(n, size)] = dim
        return self._base_with_dim_lookup[(n, size)]#.copy()

class PRMap:
    def __init__(self, name, im=None, gm=None, ms=None):
        self.name = name
        self._image = im
        self._gamemodes = gm
        self._mapsize = ms

    @property
    def mapsize(self):
        if self._mapsize is None:
            for map_inf in map_infos:
                if map_inf['code'] == self.name:
                    self._mapsize = int(map_inf['mapsize'])
                    break
        return self._mapsize

    @property
    def gamemodes(self):
        if self._gamemodes is None:
            with open(getAbsoluteResourcePath(os.path.join(jsons_dir, self.name, 'listgm.json')), 'r') as j:
                self._gamemodes = list(map(lambda i: all_gamemodes_lookup_inv[i], json.load(j)))
        return self._gamemodes

    def get_gamemode(self, name):
        p = os.path.join(jsons_dir, self.name, all_gamemodes_lookup[name] + '.json')
        if os.path.isfile(p):
            with open(getAbsoluteResourcePath(p)) as j:
                gm = json.load(j)
            return gm
        else:
            return False

    def has_gamemode(self, name):
        p = os.path.join(jsons_dir, self.name, all_gamemodes_lookup[name] + '.json')
        return os.path.isfile(p)

    @property
    def image(self):
        if self._image is None:
            self._image = Image.open(getAbsoluteResourcePath(os.path.join(images_dir, self.name + map_image_ext)))
        return self._image.copy()

all_maps_lookup = {}
for map_name in all_map_names:
    all_maps_lookup[map_name] = PRMap(map_name)

input_map_names = all_map_names + ['all']

# Colormaps from colors.yaml
try:
    with open(colormaps_file) as cf:
        colormaps = yaml.load(cf)
except FileNotFoundError:
    with open(getAbsoluteResourcePath(colormaps_int_file)) as cf:
        colormaps = yaml.load(cf)




# Overlay stiles from overlays.yaml
try:
    with open(overlays_file) as of:
        overlays = yaml.load(of)
except FileNotFoundError:
    with open(getAbsoluteResourcePath(colormaps_int_file)) as of:
        overlays = yaml.load(of)




# Argparse
parser = argparse.ArgumentParser(description='PRMaps is used to export Project Reality maps with different layout cobinations. Specify the map names and options for the export.')
parser.add_argument(
    '-v', '--version',
    action='version',
     version='%(prog)s '+version,
    help='show version message and exit'
)
choices = input_map_names + list(all_gamemodes_lookup.keys())
parser.add_argument(
    'mapnames',
    type=str,
    metavar='map/gamemode',
    choices=choices,
    nargs='+',
    help='a list of desired map names each followed by the desired gamemode(s) you wish to export; ' + \
         'gamemodes preceding the first map are treated as if they were present after every map; ' + \
         'use the keyword \'all\' to export all maps; ' + \
         'use --list-maps to see all available maps, or --list-gamemodes to see all available gamemodes'
)
choices = input_map_names
choices.remove('all')
parser.add_argument(
    '--list-maps',
    action='version',
    version='\'' + '\' \''.join(choices) + '\'' if (len(choices)) else 'No maps are availabe.',
    help='list available maps and exit'
)
choices =  list(all_gamemodes_lookup.keys())
parser.add_argument(
    '--list-gamemodes',
    action='version',
    version='\'' + '\' \''.join(choices) + '\'' if (len(choices)) else 'No gamemodes availabe.',
    help='list available gamemodes and exit'
)
choices = list(colormaps.keys())
parser.add_argument(
    '-c', '--colormap',
    type=str,
    metavar='colormap',
    choices=choices,
    default=choices[0],
    dest='colormap_name',
    help='name of the colormap to be used when generating the maps; the colormap defines the overlay and flag colors, and background dim; default is \'' + choices[0] + '\''
)
parser.add_argument(
    '--list-colormaps',
    action='version',
    version='\'' + '\' \''.join(choices) + '\'' if (len(choices)) else 'No colormaps are availabe.',
    help='list available colormaps and exit'
)
choices = list(overlays.keys())
parser.add_argument(
    '-o', '--overlay',
    type=str,
    metavar='overlay',
    choices=choices,
    default=choices[0],
    dest='overlay_name',
    help='name of the overlay style to be used when generating the maps; default is \'' + choices[0] + '\''
)
parser.add_argument(
    '-s', '--size',
    type=int,
    metavar='1024|2048|4096',
    choices=[1024, 2048, 4096],
    default=1024,
    dest='output_size',
    help='width and height of the generated images in pixels; should be one of 1024, 2048 or 4096; default is 1024'
)
parser.add_argument(
    '--list-overlays',
    action='version',
    version='\'' + '\' \''.join(choices) + '\'' if (len(choices)) else 'No overlay sytles are availabe.',
    help='list available overlay styles and exit'
)
parser.add_argument(
    '-q', '--quality',
    type=int,
    metavar='quality',
    choices=[1,2,4,8,16],
    default=4,
    dest='antialias',
    help='drawing quality of antialiasing on the drawn images; higher values produce prettier pictures, but process slower; ' + \
         'should be a multiple of two between 1 and 16'
)
parser.add_argument(
    '-u', '--hide-uncappable',
    action='store_false',
    default=True,
    dest='draw_uncappable',
    help='prevents zero radius caps from showing in the output'
)
parser.add_argument(
    '--silent',
    action='store_false',
    default=True,
    dest='verbose',
    help='silences non-critical console output'
)
args = parser.parse_args()


# Exctract selected options
global_gamemodes = []
any_gamemode = False
if 'all' not in args.mapnames:
    for opt in args.mapnames:
        if opt in all_gamemodes_lookup:
            global_gamemodes.append(opt)
            if not any_gamemode: any_gamemode = True
        else:
            break

    selected_maps_gamemodes = []
    for opt in args.mapnames[len(global_gamemodes):]:
        if opt in all_map_names:
            selected_maps_gamemodes.append({'map': all_maps_lookup[opt], 'gamemodes': list(global_gamemodes)})
        if opt in all_gamemodes_lookup:
            if opt not in selected_maps_gamemodes[-1]['gamemodes']:
                selected_maps_gamemodes[-1]['gamemodes'].append(opt)
            if not any_gamemode: any_gamemode = True
else:
    for opt in args.mapnames:
        if opt in all_gamemodes_lookup:
            global_gamemodes.append(opt)
            if not any_gamemode: any_gamemode = True
    selected_maps_gamemodes = []
    for map_name in all_map_names:
        selected_maps_gamemodes.append({'map': all_maps_lookup[map_name], 'gamemodes': list(global_gamemodes)})

verbose = args.verbose
if verbose:
    add_message("Setup", False, 'header', first=True)

if not len(selected_maps_gamemodes):
    add_message('No maps provided, exiting', verbose, 'notice')
    exit()
if not any_gamemode:
    add_message('No gamemodes provided, exiting', verbose, 'notice')
    exit()


colormap = colormaps[args.colormap_name]
if verbose:
    add_message('using colormap \'{0}\''.format(args.colormap_name), False, 'notice')
overlay = overlays[args.overlay_name]
if verbose:
    add_message('using overlay style \'{0}\''.format(args.colormap_name), False, 'notice')
output_size = args.output_size
if verbose:
    add_message('generating {0}x{0} images'.format(output_size), False, 'notice')
antialias = args.antialias
if verbose:
    add_message('antialiasing quality set to {0}'.format(antialias), False, 'notice')
draw_uc = args.draw_uncappable
if verbose:
    add_message('{0} uncappable flags'.format('including' if draw_uc else 'omitting'), False, 'notice')



if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Composite overlay base
overlay_mask = False
lettering = False
grid = False
if 'overlays' in colormap:
    lettering = False
    lettering_opacity = 1
    if 'lettering' in overlay:
        if 'opacity' in overlay['lettering']:
            lettering_opacity = overlay['lettering']['opacity']
        if 'name' not in overlay['lettering']:
            add_message('Incorrect overlay style, missing lettering image path; exiting', verbose, 'fail')
            exit()
        if lettering_opacity != 0:
            lettering = Image.open(getAbsoluteResourcePath(os.path.join(overlays_dir, overlay['lettering']['name'] + overlay_image_ext))).split()[-1]
            lettering = lettering.point(lambda i: i * lettering_opacity)

    grid = False
    grid_opacity = 1
    if 'grid' in overlay:
        if 'opacity'  in overlay['grid']:
            grid_opacity = overlay['grid']['opacity']
        if 'name' not in overlay['grid']:
            add_message('Incorrect overlay style, missing grid image path; exiting"', verbose, 'fail')
            exit()
        if grid_opacity != 0:
            grid = Image.open(getAbsoluteResourcePath((os.path.join(overlays_dir, overlay['grid']['name'] + overlay_image_ext)))).split()[-1]
            grid = grid.point(lambda i: i * grid_opacity)

    if lettering and grid:
        lettering.paste(grid, mask=grid)
        overlay_mask = lettering
    elif lettering:
        overlay_mask = lettering
    elif grid:
        overlay_mask = grid

    if overlay_mask:
        w = overlay_mask.size[0]
        # noinspection PyUnresolvedReferences
        overlay_mask = overlay_mask.resize((output_size, output_size), resample=Image.BILINEAR if (w > output_size) else Image.CUBIC)

cache = OverlayCache(overlay_mask, colormap, overlay['grid']['opacity'] if grid else False, output_size)

# Generate each map image
for selection in selected_maps_gamemodes:
    prmap = selection['map']
    selected_gamemodes = selection['gamemodes']

    if verbose:
        add_message('Exporting map \'{0}\'...'.format(prmap.name), False, 'header')

    if not len(selected_gamemodes):
        if verbose:
            add_message('Skipping \'{0}\' as no gamemodes were selected'.format(prmap.name), False, 'notice', 1)
        continue
    mapsize = prmap.mapsize
    scale = output_size / mapsize

    gamepath = os.path.join(output_dir, prmap.name)
    outgamename = prmap.name

    # noinspection PyRedeclaration
    background_img = prmap.image
    bg_size = background_img.size[0]
    background_img = background_img.resize((output_size, output_size), resample=Image.BILINEAR if (bg_size > output_size) else Image.CUBIC)

    for gamemode_name in selected_gamemodes:
        gamemode = prmap.get_gamemode(gamemode_name)
        if not gamemode and verbose:
            add_message('gamemode \'{0}\' does not exist for \'{1}\''
                  .format(gamemode_name, prmap.name), False, 'notice')
            continue
        elif verbose:
            add_message('gamemode \'{0}\''.format(gamemode_name), False, 'header')

        gamemodepath = os.path.join(gamepath, gamemode_name)
        outgamemodename = outgamename + '_' + gamemode_name

        cp_lookup = {}
        for feature in gamemode['features']:
            if feature['bf2props']['class'] == 'ControlPoint':
                cp_lookup[feature['bf2props']['name']] = feature

        for k, route in enumerate(gamemode['routes']):
            add_message('Route \'{0}\'...'.format(k), False, '')
            n = k
            if 'sequence' in colormap:
                n %= len(colormap['sequence'])
                color = colormap['sequence'][n]
            else:
                color = False


            overlay_img = cache.get_composite_overlay(n, prmap.mapsize)
            route_img = background_img.copy()
            route_img.paste(overlay_img, mask=overlay_img)

            # Extract flag group information for all routes once
            flag_groups = []
            for flag_name_group in route:
                flags = [cp_lookup[s] for s in flag_name_group]
                for flag in flags:
                    x, y = list(flag['geometry']['coordinates'])
                    flag['img_coords'] = [round(x * scale), round(- y * scale)]
                    r = float(flag['geometry']['radius'])
                    if r < 7:
                        if draw_uc:
                            flag['radius'] = ceil(5 * scale)
                        else:
                            flag['radius'] = False
                    else:
                        flag['radius'] = int(round((r if r >= 7 else 0) * scale))
                    flag['name'] = flag['bf2props']['name_object']

                l = len(flags)
                if l > 1:
                    positions = [d['img_coords'] for d in flags]
                    average_pos = [round(sum(x)/l) for x in zip(*positions)]
                else:
                    average_pos = flags[0]['img_coords']
                    average_pos = [round(x) for x in average_pos]

                flag_groups.append({'flags': flags, 'avg_coords':average_pos})

            # Draw flag backgrounds
            bgcolor = False
            if color and 'flag_background_color' in color:
                bgcolor = color['flag_background_color']
            elif 'flag_background_color' in colormap:
                bgcolor = colormap['flag_background_color']
            if bgcolor and len(bgcolor) > 7 and bgcolor[-2:] == "00":
                bgcolor = False

            if bgcolor:
                for flag_group in flag_groups:
                    for flag in flag_group['flags']:
                        if flag['radius']:
                            # noinspection PyTypeChecker
                            fill_circle_centered(image    =route_img,
                                                 position =flag['img_coords'],
                                                 radius   =flag['radius']-1,
                                                 color    =bgcolor,
                                                 antialias=antialias)

            # Draw flag connection lines
            flaglinecolor = False
            if color and 'flag_line_color' in color:
                flaglinecolor = color['flag_line_color']
            elif 'flag_line_color' in colormap:
                flaglinecolor = colormap['flag_circle_color']
            if flaglinecolor and len(flaglinecolor) > 7 and flaglinecolor[-2:] == "00":
                flaglinecolor = False
            flagline = False
            if color and 'flag_line_width' in color:
                flagline = round(color['flag_line_width'])
            elif 'flag_line_width' in colormap:
                flagline = round(colormap['flag_line_width'])

            if flaglinecolor and flagline:
                for flag_group in flag_groups:
                    if draw_uc and len(flag_group['flags']) <= 1: continue
                    for flag in flag_group['flags']:
                        if flag['radius']:
                            draw_line(image    =route_img,
                                      points   =flag_group['avg_coords'] + flag['img_coords'],
                                      thickness=flagline,
                                      color    =flaglinecolor,
                                      antialias=antialias)

            # Draw route lines
            routecolor = False
            if color and 'route_color' in color:
                routecolor = color['route_color']
            elif 'route_color' in colormap:
                routecolor = colormap['route_color']
            if routecolor and len(routecolor) > 7 and routecolor[-2:] == "00":
                routecolor = False

            routeline = False
            if color and 'route_width' in color:
                routeline = round(color['route_width'])
            elif 'route_width' in colormap:
                routeline = round(colormap['route_width'])

            if routecolor and routeline:
                for i in range(len(flag_groups)-1):
                    draw_line(image    =route_img,
                              points   =flag_groups[i]['avg_coords'] + flag_groups[i+1]['avg_coords'],
                              thickness=routeline,
                              color    =routecolor,
                              antialias=antialias)

            # Draw flag circles
            flagcolor = False
            if color and 'flag_circle_color' in color:
                flagcolor = color['flag_circle_color']
            elif 'flag_circle_color' in colormap:
                flagcolor = colormap['flag_circle_color']
            if flagcolor and len(flagcolor) > 7 and flagcolor[-2:] == "00":
                flagcolor = False

            flagoutline = False
            if color and 'flag_circle_width' in color:
                flagoutline = round(color['flag_circle_width'])
            elif 'flag_circle_width' in colormap:
                flagoutline = round(colormap['flag_circle_width'])

            if flagcolor and flagoutline:
                for flag_group in flag_groups:
                    for flag in flag_group['flags']:
                        if flag['radius']:
                            # noinspection PyTypeChecker
                            draw_circle_centered(image=route_img,
                                                 position=flag['img_coords'],
                                                 radius=flag['radius'],
                                                 thickness=flagoutline,
                                                 color=flagcolor,
                                                 antialias=antialias)

            # Draw flag texts
            textcolor = False
            if color and 'text_color' in color:
                textcolor = color['text_color']
            elif 'text_color' in colormap:
                textcolor = colormap['text_color']
            if bgcolor and len(routecolor) > 7 and textcolor[-2:] == "00":
                textcolor = False

            textsize = False
            if color and 'text_size' in color:
                textsize = round(color['text_size'])
            elif 'text_size' in colormap:
                textsize = round(colormap['text_size'])

            fontame = False
            if color and 'text_font' in color:
                fontame = color['text_font']
            elif 'text_font' in colormap:
                fontame = colormap['text_font']
            if not fontame:
                fontname = font_default

            if textcolor and textsize:
                for flag_group in flag_groups:
                    for flag in flag_group['flags']:
                        if flag['radius']:
                            x, y = flag['img_coords']
                            y -= round(flag['radius'] + 10 * scale)
                            draw_text(image=route_img,
                                      text=flag['name'],
                                      position=[x,y],
                                      font=get_scaled_font(fontame, textsize, antialias),
                                      color=textcolor,
                                      anchor=('c','b'),
                                      antialias=antialias)

            outname = '{0}_r{1}_{2}{3}'.format(outgamemodename, k, output_size, output_ext)
            filename = os.path.join(gamemodepath, outname)
            ex = os.path.isfile(filename)
            os.makedirs(gamemodepath, exist_ok=True)
            route_img.save(filename, output_format)
            export_cntr += 1
            add_message('{0} {1}{2}'.format('saved as' if not ex else 'updated', '...' if len(filename)>50 else '', filename[-80:]), True, 'success')

exec_end = dtimer()
exec_time = exec_end - exec_start

add_message('Export complete', False, 'header')
add_message('{:} images created in {:.3} seconds'.format(export_cntr, exec_time), False, 'notice')
stdout.write('\n')
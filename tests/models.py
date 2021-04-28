﻿"""Creates models used by the test suite."""
__license__ = 'MIT'


import mph


def capacitor():
    """Creates the tutorial model."""
    model = mph.session.client.create('capacitor')

    parameters = model/'parameters'
    (parameters/'Parameters 1').rename('parameters')
    model.parameter('U', '1[V]')
    model.description('U', 'applied voltage')
    model.parameter('d', '2[mm]')
    model.description('d', 'electrode spacing')
    model.parameter('l', '10[mm]')
    model.description('l', 'plate length')
    model.parameter('w', '2[mm]')
    model.description('w', 'plate width')

    functions = model/'functions'
    step = functions.create('Step', name='step')
    step.property('funcname', 'step')
    step.property('location', -0.01)
    step.property('smooth', 0.01)

    components = model/'components'
    components.create(True, name='component')

    geometries = model/'geometries'
    geometry = geometries.create(2, name='geometry')
    anode = geometry.create('Rectangle', name='anode')
    anode.property('pos', ['-d/2-w/2', '0'])
    anode.property('base', 'center')
    anode.property('size', ['w', 'l'])
    cathode = geometry.create('Rectangle', name='cathode')
    cathode.property('base', 'center')
    cathode.property('pos',  ['+d/2+w/2', '0'])
    cathode.property('size', ['w', 'l'])
    vertices = geometry.create('BoxSelection', name='vertices')
    vertices.property('entitydim', 0)
    rounded = geometry.create('Fillet', name='rounded')
    rounded.property('radius', '1[mm]')
    rounded.java.selection('point').named(vertices.tag())
    medium1 = geometry.create('Rectangle', name='medium 1')
    medium1.property('pos',  ['-max(l,d+2*w)', '-max(l,d+2*w)'])
    medium1.property('size', ['max(l,d+2*w)', 'max(l,d+2*w)*2'])
    medium2 = geometry.create('Rectangle', name='medium 2')
    medium2.property('pos',  ['0', '-max(l,d+2*w)'])
    medium2.property('size', ['max(l,d+2*w)', 'max(l,d+2*w)*2'])
    axis = geometry.create('Polygon', name='axis')
    axis.property('type', 'open')
    axis.property('source', 'table')
    axis.property('table', [
        ['-d/2', '0'],
        ['-d/4', '0'],
        ['0',    '0'],
        ['+d/4', '0'],
        ['+d/2', '0'],
    ])
    model.build(geometry)

    coordinates = model/'coordinates'
    (coordinates/'Boundary System 1').rename('boundary system')

    views = model/'views'
    view = views/'View 1'
    view.rename('view')
    view.java.axis().label('axis')
    view.java.axis().set('xmin', -0.01495)
    view.java.axis().set('xmax', +0.01495)
    view.java.axis().set('ymin', -0.01045)
    view.java.axis().set('ymax', +0.01045)

    selections = model/'selections'
    anode_volume = selections.create('Disk', name='anode volume')
    anode_volume.property('posx', '-d/2-w/2')
    anode_volume.property('r', 'w/10')
    anode_surface = selections.create('Adjacent', name='anode surface')
    anode_surface.property('input', [anode_volume])
    cathode_volume = selections.create('Disk', name='cathode volume')
    cathode_volume.property('posx', '+d/2+w/2')
    cathode_volume.property('r', 'w/10')
    cathode_surface = selections.create('Adjacent', name='cathode surface')
    cathode_surface.property('input', [cathode_volume])
    medium1 = selections.create('Disk', name='medium 1')
    medium1.property('posx', '-2*d/10')
    medium1.property('r', 'd/10')
    medium2 = selections.create('Disk', name='medium 2')
    medium2.property('posx', '+2*d/10')
    medium2.property('r', 'd/10')
    media = selections.create('Union', name='media')
    media.property('input', [medium1, medium2])
    domains = selections.create('Explicit', name='domains')
    domains.java.all()
    exterior = selections.create('Adjacent', name='exterior')
    exterior.property('input', [domains])
    axis = selections.create('Box', name='axis')
    axis.property('entitydim', 1)
    axis.property('xmin', '-d/2-w/10')
    axis.property('xmax', '+d/2+w/10')
    axis.property('ymin', '-l/20')
    axis.property('ymax', '+l/20')
    axis.property('condition', 'inside')
    center = selections.create('Disk', name='center')
    center.property('entitydim', 0)
    center.property('r', 'd/10')
    probe1 = selections.create('Disk', name='probe 1')
    probe1.property('entitydim', 0)
    probe1.property('posx', '-d/4')
    probe1.property('r', 'd/10')
    probe2 = selections.create('Disk', name='probe 2')
    probe2.property('entitydim', 0)
    probe2.property('posx', '+d/4')
    probe2.property('r', 'd/10')

    physics = model/'physics'
    es = physics.create('Electrostatics', geometry, name='electrostatic')
    es.java.field('electricpotential').field('V_es')
    es.java.selection().named(media.tag())
    es.java.prop('d').set('d', 'l')
    (es/'Charge Conservation 1').rename('Laplace equation')
    (es/'Zero Charge 1').rename('zero charge')
    (es/'Initial Values 1').rename('initial values')
    anode = es.create('ElectricPotential', 1, name='anode')
    anode.java.selection().named(anode_surface.tag())
    anode.property('V0', '+U/2')
    cathode = es.create('ElectricPotential', 1, name='cathode')
    cathode.java.selection().named(cathode_surface.tag())
    cathode.property('V0', '-U/2')
    ec = physics.create('ConductiveMedia', geometry, name='electric currents')
    ec.java.field('electricpotential').field('V_ec')
    ec.java.selection().named(media.tag())
    ec.java.prop('d').set('d', 'l')
    (ec/'Current Conservation 1').rename('current conservation')
    (ec/'Electric Insulation 1').rename('insulation')
    (ec/'Initial Values 1').rename('initial values')
    anode = ec.create('ElectricPotential', 1, name='anode')
    anode.java.selection().named(anode_surface.tag())
    anode.property('V0', '+U/2*step(t[1/s])')
    cathode = ec.create('ElectricPotential', 1, name='cathode')
    cathode.java.selection().named(cathode_surface.tag())
    cathode.property('V0', '-U/2*step(t[1/s])')

    materials = model/'materials'
    medium1 = materials.create('Common', name='medium 1')
    medium1.java.selection().named((model/'selections'/'medium 1').tag())
    medium1.java.propertyGroup('def').set('relpermittivity',
        ['1', '0', '0', '0', '1', '0', '0', '0', '1'])
    medium1.java.propertyGroup('def').set('relpermittivity_symmetry', '0')
    medium1.java.propertyGroup('def').set('electricconductivity',
        ['1e-10', '0', '0', '0', '1e-10', '0', '0', '0', '1e-10'])
    medium1.java.propertyGroup('def').set('electricconductivity_symmetry', '0')
    medium2 = materials.create('Common', name='medium 2')
    medium2.java.selection().named((model/'selections'/'medium 2').tag())
    medium2.java.propertyGroup('def').set('relpermittivity',
        ['2', '0', '0', '0', '2', '0', '0', '0', '2'])
    medium2.java.propertyGroup('def').set('relpermittivity_symmetry', '0')
    medium2.java.propertyGroup('def').set('electricconductivity',
        ['1e-10', '0', '0', '0', '1e-10', '0', '0', '0', '1e-10'])
    medium2.java.propertyGroup('def').set('electricconductivity_symmetry', '0')

    meshes = model/'meshes'
    meshes.create(geometry, name='mesh')

    studies = model/'studies'
    solutions = model/'solutions'
    batches = model/'batches'
    study = studies.create(name='static')
    study.java.setGenPlots(False)
    study.java.setGenConv(False)
    step = study.create('Stationary', name='stationary')
    step.property('activate', [
        physics/'electrostatic', 'on',
        physics/'electric currents', 'off',
        'frame:spatial1', 'on',
        'frame:material1', 'on',
    ])
    solution = solutions.create(name='electrostatic solution')
    solution.java.study(study.tag())
    solution.java.attach(study.tag())
    solution.create('StudyStep', name='equations')
    solution.create('Variables', name='variables')
    solver = solution.create('Stationary', name='stationary solver')
    (solver/'Fully Coupled').rename('fully coupled')
    (solver/'Advanced').rename('advanced options')
    (solver/'Direct').rename('direct solver')
    study = studies.create(name='relaxation')
    study.java.setGenPlots(False)
    study.java.setGenConv(False)
    step = study.create('Transient', name='time-dependent')
    step.property('tlist', 'range(0, 0.01, 1)')
    step.property('activate', [
        physics/'electrostatic', 'off',
        physics/'electric currents', 'on',
        'frame:spatial1', 'on',
        'frame:material1', 'on',
    ])
    solution = solutions.create(name='time-dependent solution')
    solution.java.study(study.tag())
    solution.java.attach(study.tag())
    solution.create('StudyStep', name='equations')
    variables = solution.create('Variables', name='variables')
    variables.property('clist', ['range(0, 0.01, 1)', '0.001[s]'])
    solver = solution.create('Time', name='time-dependent solver')
    solver.property('tlist', 'range(0, 0.01, 1)')
    (solver/'Fully Coupled').rename('fully coupled')
    (solver/'Advanced').rename('advanced options')
    (solver/'Direct').rename('direct solver')
    study = studies.create(name='sweep')
    study.java.setGenPlots(False)
    study.java.setGenConv(False)
    step = study.create('Parametric', name='parameter sweep')
    step.property('pname', ['d'])
    step.property('plistarr', ['1 2 3'])
    step.property('punit', ['mm'])
    step = study.create('Transient', name='time-dependent')
    step.property('activate', [
        physics/'electrostatic', 'off',
        physics/'electric currents', 'on',
        'frame:spatial1', 'on',
        'frame:material1', 'on',
    ])
    step.property('tlist', 'range(0, 0.01, 1)')
    solution = solutions.create(name='parametric solution')
    solution.java.study(study.tag())
    solution.java.attach(study.tag())
    solution.create('StudyStep', name='equations')
    variables = solution.create('Variables', name='variables')
    variables.property('clist', ['range(0, 0.01, 1)', '0.001[s]'])
    solver = solution.create('Time', name='time-dependent solver')
    solver.property('tlist', 'range(0, 0.01, 1)')
    (solver/'Fully Coupled').rename('fully coupled')
    (solver/'Advanced').rename('advanced options')
    (solver/'Direct').rename('direct solver')
    sols = solutions.create(name='parametric solutions')
    sols.java.study(study.tag())
    batch = batches.create('Parametric', name='parametric sweep')
    sequence = batch.create('Solutionseq', name='parametric solution')
    sequence.property('seq', solution)
    sequence.property('psol', sols)
    sequence.property('param', ['"d","0.001"', '"d","0.002"', '"d","0.003"'])
    batch.java.study(study.tag())
    batch.java.attach(study.tag())
    batch.property('control', model/'studies'/'sweep'/'parameter sweep')
    batch.property('pname', ['d'])
    batch.property('plistarr', ['1 2 3'])
    batch.property('punit', ['mm'])
    batch.property('err', True)

    datasets = model/'datasets'
    (datasets/'static//electrostatic solution').rename('electrostatic')
    (datasets/'relaxation//time-dependent solution').rename('time-dependent')
    (datasets/'sweep//parametric solution').rename('sweep/solution')
    (datasets/'sweep//solution').java.comments(
        'This auto-generated feature could be removed, as it is not '
        'really needed. It was left in the model for the purpose of '
        'testing MPh. Its name contains a forward slash, which MPh '
        'uses to denote parent–child relationships in the node hierarchy.')
    (datasets/'sweep//parametric solutions').rename('parametric sweep')

    tables = model/'tables'
    tables.create('Table', name='electrostatic')
    tables.create('Table', name='time-dependent')
    tables.create('Table', name='parametric')

    evaluations = model/'evaluations'
    evaluation = evaluations.create('EvalGlobal', name='electrostatic')
    evaluation.property('probetag', 'none')
    evaluation.property('table', tables/'electrostatic')
    evaluation.property('expr',  ['2*es.intWe/U^2'])
    evaluation.property('unit',  ['pF'])
    evaluation.property('descr', ['capacitance'])
    evaluation.java.setResult()
    evaluation = evaluations.create('EvalGlobal', name='time-dependent')
    evaluation.property('data', datasets/'time-dependent')
    evaluation.property('probetag', 'none')
    evaluation.property('table', tables/'time-dependent')
    evaluation.property('expr',  ['2*ec.intWe/U^2'])
    evaluation.property('unit',  ['pF'])
    evaluation.property('descr', ['capacitance'])
    evaluation.java.setResult()
    evaluation = evaluations.create('EvalGlobal', name='parametric')
    evaluation.property('data', 'dset4')
    evaluation.property('probetag', 'none')
    evaluation.property('table', tables/'parametric')
    evaluation.property('expr',  ['2*ec.intWe/U^2'])
    evaluation.property('unit',  ['pF'])
    evaluation.property('descr', ['capacitance'])
    evaluation.java.setResult()

    plots = model/'plots'
    plots.java.setOnlyPlotWhenRequested(True)
    plot = plots.create('PlotGroup2D', name='electrostatic field')
    plot.property('titletype', 'manual')
    plot.property('title', 'Electrostatic field')
    plot.property('showlegendsunit', True)
    surface = plot.create('Surface', name='field strength')
    surface.property('resolution', 'normal')
    surface.property('expr', 'es.normE')
    contour = plot.create('Contour', name='equipotentials')
    contour.property('number', 10)
    contour.property('coloring', 'uniform')
    contour.property('colorlegend', False)
    contour.property('color', 'gray')
    contour.property('resolution', 'normal')
    plot = plots.create('PlotGroup2D', name='time-dependent field')
    plot.property('data', datasets/'time-dependent')
    plot.property('titletype', 'manual')
    plot.property('title', 'Time-dependent field')
    plot.property('showlegendsunit', True)
    surface = plot.create('Surface', name='field strength')
    surface.property('expr', 'ec.normE')
    surface.property('resolution', 'normal')
    contour = plot.create('Contour', name='equipotentials')
    contour.property('expr', 'V_ec')
    contour.property('number', 10)
    contour.property('coloring', 'uniform')
    contour.property('colorlegend', False)
    contour.property('color', 'gray')
    contour.property('resolution', 'normal')
    plot = plots.create('PlotGroup1D', name='evolution')
    plot.property('data', datasets/'time-dependent')
    plot.property('titletype', 'manual')
    plot.property('title', 'Evolution of field over time')
    plot.property('xlabel', 't (s)')
    plot.property('xlabelactive', True)
    plot.property('ylabel', '|E| (V/m)')
    plot.property('ylabelactive', True)
    graph = plot.create('PointGraph', name='medium 1')
    graph.java.selection().named((selections/'probe 1').tag())
    graph.property('expr', 'ec.normE')
    graph.property('linecolor', 'blue')
    graph.property('linewidth', 3)
    graph.property('linemarker', 'point')
    graph.property('markerpos', 'datapoints')
    graph.property('legend', True)
    graph.property('legendmethod', 'manual')
    graph.property('legends', ['medium 1'])
    graph = plot.create('PointGraph', name='medium 2')
    graph.java.selection().named((selections/'probe 2').tag())
    graph.property('expr', 'ec.normE')
    graph.property('linecolor', 'red')
    graph.property('linewidth', 3)
    graph.property('linemarker', 'point')
    graph.property('markerpos', 'datapoints')
    graph.property('legend', True)
    graph.property('legendmethod', 'manual')
    graph.property('legends', ['medium 2'])
    plot = plots.create('PlotGroup2D', name='sweep')
    plot.property('data', datasets/'parametric sweep')
    plot.property('titletype', 'manual')
    plot.property('title', 'Parameter sweep')
    plot.property('showlegendsunit', True)
    surface = plot.create('Surface', name='field strength')
    surface.property('expr', 'ec.normE')
    surface.property('resolution', 'normal')
    contour = plot.create('Contour', name='equipotentials')
    contour.property('expr', 'V_ec')
    contour.property('number', 10)
    contour.property('coloring', 'uniform')
    contour.property('colorlegend', False)
    contour.property('color', 'gray')
    contour.property('resolution', 'normal')

    exports = model/'exports'
    data = exports.create('Data', name='data')
    data.property('expr', ['es.Ex', 'es.Ey', 'es.Ez'])
    data.property('unit', ['V/m', 'V/m', 'V/m'])
    data.property('descr', ['x-component', 'y-component', 'z-component'])
    data.property('filename', 'data.txt')
    image = exports.create('Image', name='image')
    image.property('sourceobject', plots/'electrostatic field')
    image.property('filename', 'image.png')
    image.property('size', 'manualweb')
    image.property('unit', 'px')
    image.property('height', '720')
    image.property('width', '720')
    image.property('lockratio', 'off')
    image.property('resolution', '96')
    image.property('antialias', 'on')
    image.property('zoomextents', 'off')
    image.property('fontsize', '12')
    image.property('customcolor', [1, 1, 1])
    image.property('background', 'color')
    image.property('gltfincludelines', 'on')
    image.property('title1d', 'on')
    image.property('legend1d', 'on')
    image.property('logo1d', 'on')
    image.property('options1d', 'on')
    image.property('title2d', 'on')
    image.property('legend2d', 'on')
    image.property('logo2d', 'off')
    image.property('options2d', 'on')
    image.property('title3d', 'on')
    image.property('legend3d', 'on')
    image.property('logo3d', 'on')
    image.property('options3d', 'off')
    image.property('axisorientation', 'on')
    image.property('grid', 'on')
    image.property('axes1d', 'on')
    image.property('axes2d', 'on')
    image.property('showgrid', 'on')
    image.property('target', 'file')
    image.property('qualitylevel', '92')
    image.property('qualityactive', 'off')
    image.property('imagetype', 'png')
    image.property('lockview', 'off')

    return model

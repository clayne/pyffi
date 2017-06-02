from tests.scripts.nif import call_niftoaster
import os
import shutil

from . import BaseFileTestCase
import nose
import pyffi
from pyffi.spells import Toaster
from pyffi.formats.nif import NifFormat

from tests.utils import assert_tuple_values


class TestCollisionOptimisation(BaseFileTestCase):

    def setUp(self):
        super(TestCollisionOptimisation, self).setUp()
        self.src_name = "test_opt_collision_to_boxshape.nif"
        self.src_file = os.path.join(self.input_files, self.src_name)
        self.dest_file = os.path.join(self.out, self.src_name)
        shutil.copyfile(self.src_file, self.dest_file)
        assert os.path.exists(self.dest_file)

    def test_box_optimisation(self):
        data = NifFormat.Data()
        stream = open(self.src_file, "rb")
        data.read(stream)
        # check initial data
        shape = data.roots[0].collision_object.body.shape
        nose.tools.assert_equals(shape.data.num_vertices, 8)
        sub_shape = shape.sub_shapes[0]
        nose.tools.assert_equals(sub_shape.num_vertices, 8)
        nose.tools.assert_equals(sub_shape.material.material, 0)

        # run the spell that optimizes this
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=data)
        spell.recurse()
        """
        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [Scene Root] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        optimized box collision
        # pyffi.toaster:INFO:    ~~~ NiNode [Door] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [Door] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [Door] ~~~
        # pyffi.toaster:INFO:    ~~~ NiNode [WoodBeam01] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [WoodBeam01] ~~~
        # pyffi.toaster:INFO:    ~~~ NiNode [WoodBeam02] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [WoodBeam02] ~~~
        # pyffi.toaster:INFO:    ~~~ NiNode [WoodBeam03] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [WoodBeam03] ~~~
        # pyffi.toaster:INFO:    ~~~ NiNode [Rusty Metal Bottom] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [Rusty Metal Bottom] ~~~
        # pyffi.toaster:INFO:    ~~~ NiNode [Rusty Metal Top] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [Rusty Metal Top] ~~~
        """

        # check optimized data
        shape = data.roots[0].collision_object.body.shape
        nose.tools.assert_equals(shape.material.material, 0)
        nose.tools.assert_true(isinstance(shape, NifFormat.bhkBoxShape))


class TestBoxCollisionOptimisation(BaseFileTestCase):

    def setUp(self):
        super(TestBoxCollisionOptimisation, self).setUp()
        self.src_name = "test_opt_collision_unpacked.nif"
        super(TestBoxCollisionOptimisation, self).readFile()
        super(TestBoxCollisionOptimisation, self).readNifData()

    def test_box_from_unpacked_collision_optimisation(self):
        """Test Box conversion from unpacked collision"""

        # check initial data
        shape = self.data.roots[0].collision_object.body.shape
        nose.tools.assert_equals(shape.strips_data[0].num_vertices, 24)
        nose.tools.assert_equals(shape.material.material, 9)

        # run the spell that optimizes this
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=self.data)
        spell.recurse()

        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [TestBhkNiTriStripsShape] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        optimized box collision
        # pyffi.toaster:INFO:    ~~~ NiTriShape [Stuff] ~~~

        # check optimized data
        shape = self.data.roots[0].collision_object.body.shape
        nose.tools.assert_true(isinstance(shape, NifFormat.bhkConvexTransformShape))
        nose.tools.assert_equals(shape.material.material, 9)


class TestPackedBoxCollisionOptimisation(BaseFileTestCase):

    def setUp(self):
        super(TestPackedBoxCollisionOptimisation, self).setUp()
        self.src_name = "test_opt_collision_packed.nif"
        super(TestPackedBoxCollisionOptimisation, self).readFile()
        super(TestPackedBoxCollisionOptimisation, self).readNifData()

    def test_box_from_packed_collision_optimisation(self):
        """Test Box conversion from packed collision"""

        # check initial data
        shape = self.data.roots[0].collision_object.body.shape
        nose.tools.assert_equals(shape.data.num_vertices, 24)
        nose.tools.assert_equals(shape.sub_shapes[0].num_vertices, 24)
        nose.tools.assert_equals(shape.sub_shapes[0].material.material, 9)

        # run the spell that optimizes this
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=self.data)
        spell.recurse()
        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [TestBhkPackedNiTriStripsShape] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        optimized box collision
        # pyffi.toaster:INFO:    ~~~ NiTriShape [Stuff] ~~~

        # check optimized data
        shape = self.data.roots[0].collision_object.body.shape
        nose.tools.assert_equals(shape.material.material, 9)
        nose.tools.assert_true(isinstance(shape, NifFormat.bhkConvexTransformShape))
        nose.tools.assert_true(isinstance(shape.shape, NifFormat.bhkBoxShape))

    def test_box_from_mopp_collision_optimisation(self):
        """Test Box conversion from mopp collision"""

        # check initial data
        shape = self.data.roots[0].collision_object.body.shape
        nose.tools.assert_equals(shape.data.num_vertices, 24)
        nose.tools.assert_equals(shape.sub_shapes[0].num_vertices, 24)
        nose.tools.assert_equals(shape.sub_shapes[0].material.material, 9)

        # run the spell that optimizes this
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=self.data)
        spell.recurse()
        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [TestBhkMoppBvTreeShape] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        ~~~ bhkMoppBvTreeShape [] ~~~
        # pyffi.toaster:INFO:          optimized box collision
        # pyffi.toaster:INFO:    ~~~ NiTriShape [Stuff] ~~~

        # check optimized data
        shape = self.data.roots[0].collision_object.body.shape
        nose.tools.assert_equals(shape.material.material, 9)
        nose.tools.assert_equals(shape.shape.material.material, 9)
        nose.tools.assert_true(isinstance(shape, NifFormat.bhkConvexTransformShape))
        nose.tools.assert_true(isinstance(shape.shape, NifFormat.bhkBoxShape))


class TestNotBoxCollisionOptimisation(BaseFileTestCase):

    def setUp(self):
        super(TestNotBoxCollisionOptimisation, self).setUp()
        self.src_name = "test_opt_collision_to_boxshape_notabox.nif"
        super(TestNotBoxCollisionOptimisation, self).readFile()
        super(TestNotBoxCollisionOptimisation, self).readNifData()

    def test_box_from_packed_collision_optimisation(self):
        """Test that a collision mesh which is not a box, but whose vertices form a box, is not converted to a box."""

        # check initial data
        nose.tools.assert_equals(self.data.roots[0].collision_object.body.shape.__class__.__name__, 'bhkMoppBvTreeShape')

        # run the box spell
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=self.data)
        spell.recurse()
        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [no_box_opt_test] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        ~~~ bhkMoppBvTreeShape [] ~~~

        # check that we still have a mopp collision, and not a box collision
        nose.tools.assert_equals(self.data.roots[0].collision_object.body.shape.__class__.__name__, 'bhkMoppBvTreeShape')


class TestMoppCollisionOptimisation(BaseFileTestCase):
    def setUp(self):
        super(TestMoppCollisionOptimisation, self).setUp()
        self.src_name = "test_opt_collision_complex_mopp.nif"
        super(TestMoppCollisionOptimisation, self).readFile()
        super(TestMoppCollisionOptimisation, self).readNifData()

    def test_optimise_collision_complex_mopp(self):

        # check initial data
        shape = self.data.roots[0].collision_object.body.shape.shape
        nose.tools.assert_equals(shape.sub_shapes[0].num_vertices, 53)
        nose.tools.assert_equals(shape.data.num_vertices, 53)
        nose.tools.assert_equals(shape.data.num_triangles, 102)

        hktriangle = self.data.roots[0].collision_object.body.shape.shape.data.triangles[-1]
        triangle = hktriangle.triangle
        nose.tools.assert_equals(hktriangle.welding_info, 18924)

        assert_tuple_values((triangle.v_1, triangle.v_2, triangle.v_3), (13, 17, 5))
        normal = hktriangle.normal
        assert_tuple_values((-0.9038461, 0.19667668, - 0.37997436), (normal.x, normal.y, normal.z))

        # run the spell that fixes this
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionGeometry(data=self.data)
        spell.recurse()  # doctest: +REPORT_NDIFF

        # check optimized data
        shape = self.data.roots[0].collision_object.body.shape.shape
        nose.tools.assert_equals(shape.sub_shapes[0].num_vertices, 51)
        nose.tools.assert_equals(shape.data.num_vertices, 51)
        nose.tools.assert_equals(shape.data.num_triangles, 98)

        hktriangle = self.data.roots[0].collision_object.body.shape.shape.data.triangles[-1]

        triangle = hktriangle.triangle
        assert_tuple_values((triangle.v_1, triangle.v_2, triangle.v_3), (12, 16, 4))
        nose.tools.assert_equals(hktriangle.welding_info, 18924)
        assert_tuple_values((-0.9038461, 0.19667668, - 0.37997436), (normal.x, normal.y, normal.z))

        """
            pyffi.toaster: INFO:--- opt_collisiongeometry ---
            pyffi.toaster: INFO:  ~~~ NiNode[Scene Root] ~~~
            pyffi.toaster: INFO:    ~~~ bhkCollisionObject[] ~~~
            pyffi.toaster: INFO:      ~~~ bhkRigidBody[] ~~~
            pyffi.toaster: INFO:        ~~~ bhkMoppBvTreeShape[]~~~
            pyffi.toaster: INFO:          optimizing mopp
            pyffi.toaster: INFO:          removing duplicate vertices
            pyffi.toaster: INFO:          (processing subshape 0)
            pyffi.toaster: INFO:          (num vertices in collision shape was 53 and is now 51)
            pyffi.toaster: INFO:          removing duplicate triangles
            pyffi.toaster: INFO:          (num triangles in collision shape was 102 and is now 98)
            Mopper.Copyright(c)
            2008, NIF
            File
            Format
            Library and Tools.
            All
            rights
            reserved.
            < BLANKLINE >
            Options:
            --help
            for usage help
                --license
                for licensing details
    
            < BLANKLINE >
            Mopper
            uses
            havok.Copyright
            1999 - 2008
            Havok.com
            Inc.( and its
            Licensors).
            All
            Rights
            Reserved.See
            www.havok.com
            for details.
                < BLANKLINE >
            < BLANKLINE >
            pyffi.toaster: INFO:    ~~~ NiTriShape[]
            ~~~
        """


class TestUnpackedCollisionOptimisation(BaseFileTestCase):

    def setUp(self):
        super(TestUnpackedCollisionOptimisation, self).setUp()
        self.src_name = "test_opt_collision_unpacked.nif"
        super(TestUnpackedCollisionOptimisation, self).readFile()
        super(TestUnpackedCollisionOptimisation, self).readNifData()

    def test_optimise_collision_complex_mopp(self):
        """Test unpacked collision """

        # check initial data
        strip = self.data.roots[0].collision_object.body.shape.strips_data[0]
        nose.tools.assert_equals(strip.num_vertices, 24)
        nose.tools.assert_equals(strip.num_triangles, 32)

        # run the spell
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionGeometry(data=self.data)
        spell.recurse()  # doctest: +REPORT_NDIFF

        """
        pyffi.toaster: INFO:--- opt_collisiongeometry - --
        pyffi.toaster: INFO:  ~~~ NiNode[TestBhkNiTriStripsShape] ~~~
        pyffi.toaster: INFO:    ~~~ bhkCollisionObject[] ~~~
        pyffi.toaster: INFO:      ~~~ bhkRigidBodyT[] ~~~
        pyffi.toaster: INFO:        packing collision
        pyffi.toaster: INFO:        adding mopp
        """
        # check optimized data
        shape = self.data.roots[0].collision_object.body.shape.shape
        nose.tools.assert_equals(shape.sub_shapes[0].num_vertices, 8)
        nose.tools.assert_equals(shape.data.num_vertices, 8)
        nose.tools.assert_equals(shape.data.num_triangles, 12)

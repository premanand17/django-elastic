''' Test for Elastic authorization & authentication'''
from django.test import TestCase
from elastic.elastic_settings import ElasticSettings
from django.conf import settings


class ElasticAuthTest(TestCase):

    def setUp(self):
        if 'pydgin_auth' in settings.INSTALLED_APPS:
            from pydgin_auth.elastic_model_factory import ElasticPermissionModelFactory
            from django.contrib.auth.models import Group
            # create elastic models
            ElasticPermissionModelFactory.create_dynamic_models()
            # create the default group READ
            Group.objects.get_or_create(name='READ')

    def tearDown(self):
        if 'pydgin_auth' in settings.INSTALLED_APPS:
            from pydgin_auth.elastic_model_factory import ElasticPermissionModelFactory
            from django.contrib.auth.models import Group, User, Permission

            Group.objects.filter().delete()
            User.objects.filter().delete()
            Permission.objects.filter().delete()

    def test_search_props(self):

        if 'pydgin_auth' in settings.INSTALLED_APPS:
            from pydgin_auth.elastic_model_factory import ElasticPermissionModelFactory
            from django.contrib.contenttypes.models import ContentType
            from django.contrib.auth.models import Group, User, Permission
            from django.shortcuts import get_object_or_404

            search_props = ElasticSettings.search_props("ALL")

            idx = search_props['idx']
            idx_keys = search_props['idx_keys']
            idx_type = search_props['idx_type']

            self.assertIn('publications', idx, 'publications found in idx')
            self.assertIn('MARKER', idx_keys, 'MARKER found in idx_keys')
            self.assertIn('rs_merge', idx_type, 'rs_merge found in idx_type')
            self.assertIn('immunochip', idx_type, 'immunochip found in idx_type')

            # CREATE DIL group and add test_dil user to that group
            dil_group, created = Group.objects.get_or_create(name='DILX')
            self.assertTrue(created)
            dil_user = User.objects.create_user(
                username='test_dil2', email='test_dil2@test.com', password='test123')
            dil_user.groups.add(dil_group)
            self.assertTrue(dil_user.groups.filter(name='DILX').exists())

            # create permission for pathway_genesets
            test_idx = 'marker'
            test_idx_type = 'rs_merge'

            test_model = test_idx.lower() + ElasticPermissionModelFactory.PERMISSION_MODEL_NAME_TYPE_DELIMITER + \
                test_idx_type + ElasticPermissionModelFactory.PERMISSION_MODEL_TYPE_SUFFIX

            # create permissions on models and retest again to check if the idx type could be seen
            content_type, created = ContentType.objects.get_or_create(
                model=test_model, app_label="elastic",
            )

            # create permission and assign ...Generally we create via admin interface
            can_read_permission = Permission.objects.create(codename='can_read_marker-rs_merge',
                                                            name='Can Read marker-rs_merge Idx',
                                                            content_type=content_type)

            self.assertEqual('can_read_marker-rs_merge', can_read_permission.codename, "idx type permission correct")
            # as soon as the permission is set for an index, the index becomes a restricted resource
            idx_types_visible = ElasticSettings.search_props("ALL")["idx_type"]
            self.assertFalse("rs_merge" in idx_types_visible,  'rs_merge idx type not visible')

            # now grant permission to dil_user
            dil_group.permissions.add(can_read_permission)
            dil_user = get_object_or_404(User, pk=dil_user.id)
            idx_types_visible = ElasticSettings.search_props("ALL", dil_user)["idx_type"]
            print(idx_types_visible)
            self.assertTrue("rs_merge" in idx_types_visible,  'rs_merge idx type visible now')

            # create permission for pathway_genesets
            test_idx = 'gene'
            test_model = test_idx.lower() + ElasticPermissionModelFactory.PERMISSION_MODEL_SUFFIX

            # create permissions on models and retest again to check if the idx type could be seen
            content_type, created = ContentType.objects.get_or_create(
                model=test_model, app_label="elastic",
            )

            can_read_permission = Permission.objects.create(codename='can_read_gene_idx',
                                                            name='Can Read gene Idx',
                                                            content_type=content_type)

            self.assertEqual('can_read_gene_idx', can_read_permission.codename, "idx permission correct")

            idx_visible = ElasticSettings.search_props("ALL")["idx"]
            self.assertFalse("gene" in idx_visible,  'gene idx not visible')

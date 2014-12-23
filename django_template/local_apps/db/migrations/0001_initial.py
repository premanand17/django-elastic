# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CvCvtermCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('num_terms_excl_obs', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cv_cvterm_count',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CvCvtermCountWithObs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('num_terms_incl_obs', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cv_cvterm_count_with_obs',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CvLeaf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('cv_id', models.IntegerField(blank=True, null=True)),
                ('cvterm_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cv_leaf',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CvLinkCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('cv_name', models.CharField(max_length=255, blank=True)),
                ('relation_name', models.CharField(max_length=1024, blank=True)),
                ('relation_cv_name', models.CharField(max_length=255, blank=True)),
                ('num_links', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cv_link_count',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CvPathCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('cv_name', models.CharField(max_length=255, blank=True)),
                ('relation_name', models.CharField(max_length=1024, blank=True)),
                ('relation_cv_name', models.CharField(max_length=255, blank=True)),
                ('num_paths', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cv_path_count',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cvprop',
            fields=[
                ('cvprop_id', models.IntegerField(primary_key=True, serialize=False)),
                ('value', models.TextField(blank=True)),
                ('rank', models.IntegerField()),
            ],
            options={
                'db_table': 'cvprop',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CvRoot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('cv_id', models.IntegerField(blank=True, null=True)),
                ('root_cvterm_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cv_root',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CvtermDbxref',
            fields=[
                ('cvterm_dbxref_id', models.IntegerField(primary_key=True, serialize=False)),
                ('is_for_definition', models.IntegerField()),
            ],
            options={
                'db_table': 'cvterm_dbxref',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cvtermpath',
            fields=[
                ('cvtermpath_id', models.IntegerField(primary_key=True, serialize=False)),
                ('pathdistance', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cvtermpath',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CvtermRelationship',
            fields=[
                ('cvterm_relationship_id', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'cvterm_relationship',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cvtermsynonym',
            fields=[
                ('cvtermsynonym_id', models.IntegerField(primary_key=True, serialize=False)),
                ('synonym', models.CharField(max_length=1024)),
            ],
            options={
                'db_table': 'cvtermsynonym',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeatureContains',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('subject_id', models.IntegerField(blank=True, null=True)),
                ('object_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'feature_contains',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cv',
            fields=[
                ('cv_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('definition', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'cv',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cvterm',
            fields=[
                ('cvterm_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1024)),
                ('definition', models.TextField(blank=True)),
                ('is_obsolete', models.IntegerField()),
                ('is_relationshiptype', models.IntegerField()),
                ('cv', models.ForeignKey(to='db.Cv')),
            ],
            options={
                'db_table': 'cvterm',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cvtermprop',
            fields=[
                ('cvtermprop_id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.TextField()),
                ('rank', models.IntegerField()),
                ('cvterm', models.ForeignKey(to='db.Cvterm', related_name='cvtermprop_cvterm')),
                ('type', models.ForeignKey(to='db.Cvterm', related_name='cvtermprop_type')),
            ],
            options={
                'db_table': 'cvtermprop',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Db',
            fields=[
                ('db_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('urlprefix', models.CharField(max_length=255, blank=True)),
                ('url', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'db_table': 'db',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Dbxref',
            fields=[
                ('dbxref_id', models.AutoField(primary_key=True, serialize=False)),
                ('accession', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('db', models.ForeignKey(to='db.Db')),
            ],
            options={
                'db_table': 'dbxref',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('feature_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('uniquename', models.TextField()),
                ('residues', models.TextField(blank=True)),
                ('seqlen', models.IntegerField(blank=True, null=True)),
                ('md5checksum', models.CharField(max_length=32, blank=True)),
                ('is_analysis', models.BooleanField(default=False)),
                ('is_obsolete', models.BooleanField(default=False)),
                ('timeaccessioned', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('timelastmodified', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('dbxref', models.ForeignKey(blank=True, null=True, to='db.Dbxref')),
            ],
            options={
                'db_table': 'feature',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Featureloc',
            fields=[
                ('featureloc_id', models.AutoField(primary_key=True, serialize=False)),
                ('fmin', models.IntegerField(blank=True, null=True)),
                ('is_fmin_partial', models.BooleanField(default=False)),
                ('fmax', models.IntegerField(blank=True, null=True)),
                ('is_fmax_partial', models.BooleanField(default=False)),
                ('strand', models.SmallIntegerField(blank=True, null=True)),
                ('phase', models.IntegerField(blank=True, null=True)),
                ('residue_info', models.TextField(blank=True)),
                ('locgroup', models.IntegerField()),
                ('rank', models.IntegerField()),
                ('feature', models.ForeignKey(to='db.Feature', related_name='featureloc_feature')),
                ('srcfeature', models.ForeignKey(blank=True, null=True, to='db.Feature', related_name='featureloc_srcfeature')),
            ],
            options={
                'db_table': 'featureloc',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Featureprop',
            fields=[
                ('featureprop_id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.TextField(blank=True)),
                ('rank', models.IntegerField()),
                ('feature', models.ForeignKey(to='db.Feature')),
                ('type', models.ForeignKey(to='db.Cvterm')),
            ],
            options={
                'db_table': 'featureprop',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organism',
            fields=[
                ('organism_id', models.IntegerField(primary_key=True, serialize=False)),
                ('abbreviation', models.CharField(max_length=255, blank=True)),
                ('genus', models.CharField(max_length=255)),
                ('species', models.CharField(max_length=255)),
                ('common_name', models.CharField(max_length=255, blank=True)),
                ('comment', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'organism',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='feature',
            name='organism',
            field=models.ForeignKey(to='db.Organism'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='feature',
            name='type',
            field=models.ForeignKey(to='db.Cvterm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cvterm',
            name='dbxref',
            field=models.ForeignKey(to='db.Dbxref', unique=True),
            preserve_default=True,
        ),
    ]

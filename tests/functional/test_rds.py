# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import mock
from contextlib import contextmanager

import botocore.session
from tests import BaseSessionTest


class TestRDSPresignUrlInjection(BaseSessionTest):

    def setUp(self):
        super(TestRDSPresignUrlInjection, self).setUp()
        self.client = self.session.create_client('rds', 'us-west-2')

    @contextmanager
    def patch_http_layer(self, response, status_code=200):
        with mock.patch('botocore.endpoint.Session.send') as send:
            send.return_value = mock.Mock(status_code=status_code,
                                          headers={},
                                          content=response)
            yield send

    def assert_presigned_url_injected_in_request(self, body):
        self.assertIn('PreSignedUrl', body)
        self.assertNotIn('SourceRegion', body)

    def test_copy_snapshot(self):
        params = {
            'SourceDBSnapshotIdentifier': 'source-db',
            'TargetDBSnapshotIdentifier': 'target-db',
            'SourceRegion': 'us-east-1'
        }
        response_body = (
                    b'<CopyDBSnapshotResponse>'
                    b'<CopyDBSnapshotResult></CopyDBSnapshotResult>'
                    b'</CopyDBSnapshotResponse>'
        )
        with self.patch_http_layer(response_body) as send:
            self.client.copy_db_snapshot(**params)
            sent_request = send.call_args[0][0]
            self.assert_presigned_url_injected_in_request(sent_request.body)

    def test_create_db_instance_read_replica(self):
        params = {
            'SourceDBInstanceIdentifier': 'source-db',
            'DBInstanceIdentifier': 'target-db',
            'SourceRegion': 'us-east-1'
        }
        response_body = (
            b'<CreateDBInstanceReadReplicaResponse>'
            b'<CreateDBInstanceReadReplicaResult>'
            b'</CreateDBInstanceReadReplicaResult>'
            b'</CreateDBInstanceReadReplicaResponse>'
        )
        with self.patch_http_layer(response_body) as send:
            self.client.create_db_instance_read_replica(**params)
            sent_request = send.call_args[0][0]
            self.assert_presigned_url_injected_in_request(sent_request.body)
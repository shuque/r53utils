import unittest
from unittest.mock import patch, MagicMock
import boto3
import moto
from r53utils import (
    R53Error, get_client, get_caller_ref, status, generator_zones,
    generator_rrsets, ChangeBatch, name_to_zoneid, get_rrset,
    rrset_to_text, test_dns_answer, wait_for_insync, create_zone,
    change_rrsets, get_zone, get_associated_vpcs, empty_zone, delete_zone
)

class TestR53Utils(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_client = MagicMock()
        self.zone_id = '/hostedzone/Z1234567890'
        self.zone_name = 'example.com.'
        self.rr_name = 'test.example.com.'
        self.rr_type = 'A'
        self.ttl = 300
        self.rdata = ['192.0.2.1']

    def test_get_client(self):
        """Test get_client function."""
        # Test without credentials
        with patch('boto3.client') as mock_boto3:
            get_client()
            mock_boto3.assert_called_once_with('route53', config=unittest.mock.ANY)

        # Test with credentials
        creds = {
            'AccessKeyId': 'test-key',
            'SecretAccessKey': 'test-secret',
            'SessionToken': 'test-token'
        }
        with patch('boto3.client') as mock_boto3:
            get_client(creds)
            mock_boto3.assert_called_once_with(
                'route53',
                config=unittest.mock.ANY,
                aws_access_key_id=creds['AccessKeyId'],
                aws_secret_access_key=creds['SecretAccessKey'],
                aws_session_token=creds['SessionToken']
            )

    def test_get_caller_ref(self):
        """Test get_caller_ref function."""
        ref = get_caller_ref()
        self.assertTrue(ref.startswith('r53utils.'))
        self.assertTrue(len(ref) > len('r53utils.'))

    def test_status(self):
        """Test status function."""
        response = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            }
        }
        self.assertEqual(status(response), 200)

    def test_generator_zones(self):
        """Test generator_zones function."""
        mock_response = {
            'HostedZones': [
                {'Id': self.zone_id, 'Name': self.zone_name}
            ],
            'IsTruncated': False,
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        self.mock_client.list_hosted_zones_by_name.return_value = mock_response
        
        zones = list(generator_zones(self.mock_client))
        self.assertEqual(len(zones), 1)
        self.assertEqual(zones[0]['Id'], self.zone_id)
        self.assertEqual(zones[0]['Name'], self.zone_name)

    def test_generator_rrsets(self):
        """Test generator_rrsets function."""
        mock_response = {
            'ResourceRecordSets': [
                {
                    'Name': self.rr_name,
                    'Type': self.rr_type,
                    'TTL': self.ttl,
                    'ResourceRecords': [{'Value': self.rdata[0]}]
                }
            ],
            'IsTruncated': False,
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        self.mock_client.list_resource_record_sets.return_value = mock_response
        
        rrsets = list(generator_rrsets(self.mock_client, self.zone_id))
        self.assertEqual(len(rrsets), 1)
        self.assertEqual(rrsets[0]['Name'], self.rr_name)
        self.assertEqual(rrsets[0]['Type'], self.rr_type)

    def test_change_batch(self):
        """Test ChangeBatch class."""
        batch = ChangeBatch()
        
        # Test create
        batch.create(self.rr_name, self.rr_type, self.ttl, self.rdata)
        self.assertEqual(len(batch.datadict['Changes']), 1)
        self.assertEqual(batch.datadict['Changes'][0]['Action'], 'CREATE')
        
        # Test upsert
        batch.reset()
        batch.upsert(self.rr_name, self.rr_type, self.ttl, self.rdata)
        self.assertEqual(len(batch.datadict['Changes']), 1)
        self.assertEqual(batch.datadict['Changes'][0]['Action'], 'UPSERT')
        
        # Test delete
        batch.reset()
        rrset = {
            'Name': self.rr_name,
            'Type': self.rr_type,
            'TTL': self.ttl,
            'ResourceRecords': [{'Value': self.rdata[0]}]
        }
        batch.delete(rrset)
        self.assertEqual(len(batch.datadict['Changes']), 1)
        self.assertEqual(batch.datadict['Changes'][0]['Action'], 'DELETE')

    def test_name_to_zoneid(self):
        """Test name_to_zoneid function."""
        mock_response = {
            'HostedZones': [
                {'Id': self.zone_id, 'Name': self.zone_name}
            ],
            'IsTruncated': False,
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        self.mock_client.list_hosted_zones_by_name.return_value = mock_response
        
        zone_id = name_to_zoneid(self.mock_client, self.zone_name)
        self.assertEqual(zone_id, self.zone_id)

    def test_get_rrset(self):
        """Test get_rrset function."""
        mock_response = {
            'ResourceRecordSets': [
                {
                    'Name': self.rr_name,
                    'Type': self.rr_type,
                    'TTL': self.ttl,
                    'ResourceRecords': [{'Value': self.rdata[0]}]
                }
            ],
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        self.mock_client.list_resource_record_sets.return_value = mock_response
        
        rrset = get_rrset(self.mock_client, self.zone_id, self.rr_name, self.rr_type)
        self.assertEqual(rrset['Name'], self.rr_name)
        self.assertEqual(rrset['Type'], self.rr_type)

    def test_rrset_to_text(self):
        """Test rrset_to_text function."""
        rrset = {
            'Name': self.rr_name,
            'Type': self.rr_type,
            'TTL': self.ttl,
            'ResourceRecords': [{'Value': self.rdata[0]}]
        }
        expected = f"{self.rr_name} {self.ttl} IN {self.rr_type} {self.rdata[0]}"
        self.assertEqual(rrset_to_text(rrset), expected)

    def test_test_dns_answer(self):
        """Test test_dns_answer function."""
        mock_response = {
            'Nameserver': 'ns-123.awsdns-12.com',
            'Protocol': 'UDP',
            'RecordName': self.rr_name,
            'RecordType': self.rr_type,
            'RecordData': self.rdata,
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        self.mock_client.test_dns_answer.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            test_dns_answer(self.mock_client, self.zone_id, self.rr_name, self.rr_type)
            mock_print.assert_called()

    def test_wait_for_insync(self):
        """Test wait_for_insync function."""
        # Test successful case
        mock_response = {
            'ChangeInfo': {
                'Status': 'INSYNC'
            }
        }
        self.mock_client.get_change.return_value = mock_response
        
        with patch('time.sleep'):
            wait_for_insync(self.mock_client, 'change-123')
            self.mock_client.get_change.assert_called_once()

        # Test timeout case
        mock_response['ChangeInfo']['Status'] = 'PENDING'
        self.mock_client.get_change.return_value = mock_response
        
        with patch('time.sleep'):
            with self.assertRaises(R53Error):
                wait_for_insync(self.mock_client, 'change-123', timeout=1)

    def test_create_zone(self):
        """Test create_zone function."""
        mock_response = {
            'HostedZone': {
                'Id': self.zone_id,
                'Name': self.zone_name
            },
            'DelegationSet': {
                'NameServers': ['ns-1.awsdns-00.com']
            },
            'ChangeInfo': {
                'Status': 'PENDING'
            },
            'ResponseMetadata': {'HTTPStatusCode': 201}
        }
        self.mock_client.create_hosted_zone.return_value = mock_response
        
        zone_id, ns_set, caller_ref, change_info = create_zone(
            self.mock_client, self.zone_name
        )
        self.assertEqual(zone_id, self.zone_id)
        self.assertEqual(ns_set, ['ns-1.awsdns-00.com'])

    def test_change_rrsets(self):
        """Test change_rrsets function."""
        mock_response = {
            'ChangeInfo': {
                'Status': 'PENDING'
            },
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        self.mock_client.change_resource_record_sets.return_value = mock_response
        
        batch = ChangeBatch()
        batch.create(self.rr_name, self.rr_type, self.ttl, self.rdata)
        
        change_info = change_rrsets(self.mock_client, self.zone_id, batch)
        self.assertEqual(change_info['Status'], 'PENDING')

    def test_get_zone(self):
        """Test get_zone function."""
        mock_response = {
            'HostedZone': {
                'Id': self.zone_id,
                'Name': self.zone_name
            },
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        self.mock_client.get_hosted_zone.return_value = mock_response
        
        zone = get_zone(self.mock_client, self.zone_id)
        self.assertEqual(zone['Id'], self.zone_id)
        self.assertEqual(zone['Name'], self.zone_name)

    def test_get_associated_vpcs(self):
        """Test get_associated_vpcs function."""
        mock_response = {
            'VPCs': [
                {
                    'VPCRegion': 'us-west-2',
                    'VPCId': 'vpc-12345678'
                }
            ],
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        self.mock_client.get_hosted_zone.return_value = mock_response
        
        vpcs = get_associated_vpcs(self.mock_client, self.zone_id)
        self.assertEqual(len(vpcs), 1)
        self.assertEqual(vpcs[0]['VPCRegion'], 'us-west-2')
        self.assertEqual(vpcs[0]['VPCId'], 'vpc-12345678')

    def test_empty_zone(self):
        """Test empty_zone function."""
        mock_response = {
            'ChangeInfo': {
                'Status': 'PENDING'
            },
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        self.mock_client.change_resource_record_sets.return_value = mock_response
        
        # Mock generator_rrsets to return some records
        with patch('r53utils.generator_rrsets') as mock_generator:
            mock_generator.return_value = [
                {
                    'Name': 'test.example.com.',
                    'Type': 'A',
                    'TTL': 300,
                    'ResourceRecords': [{'Value': '192.0.2.1'}]
                }
            ]
            
            change_info = empty_zone(self.mock_client, self.zone_id, self.zone_name)
            self.assertEqual(change_info['Status'], 'PENDING')

    def test_delete_zone(self):
        """Test delete_zone function."""
        mock_response = {
            'ChangeInfo': {
                'Status': 'PENDING'
            },
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        self.mock_client.delete_hosted_zone.return_value = mock_response
        
        change_info = delete_zone(self.mock_client, self.zone_id)
        self.assertEqual(change_info['Status'], 'PENDING')

if __name__ == '__main__':
    unittest.main() 
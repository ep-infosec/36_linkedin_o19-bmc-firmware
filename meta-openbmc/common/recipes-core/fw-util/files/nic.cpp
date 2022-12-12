#include <iostream>
#include <string>
#include <cstring>
#include <stdio.h>
#include "fw-util.h"

#define NCSI_DATA_PAYLOAD 64
#define NIC_FW_VER_PATH "/tmp/cache_store/nic_fw_ver"

using namespace std;

typedef struct
{
  char  mfg_name[10];//manufacture name
  uint32_t mfg_id;//manufacture id
  void (*get_nic_fw)(uint8_t *, char *);
} nic_info_st;

static void
get_mlx_fw_version(uint8_t *buf, char *version)
{
  int ver_index_based = 20;
  int major = 0;
  int minor = 0;
  int revision = 0;

  major = buf[ver_index_based++];
  minor = buf[ver_index_based++];
  revision = buf[ver_index_based++] << 8;
  revision += buf[ver_index_based++];

  sprintf(version, "%d.%d.%d", major, minor, revision);
}

static void
get_bcm_fw_version(uint8_t *buf, char *version)
{
  int ver_start_index = 8;      //the index is defined in the NC-SI spec
  const int ver_end_index = 19;
  char ver[32]={0};
  int i = 0;

  for( ; ver_start_index <= ver_end_index; ver_start_index++, i++)
  {
    if ( 0 == buf[ver_start_index] )
    {
      break;
    }
    ver[i] = buf[ver_start_index];
  }

  strcat(version, ver);
}

static  nic_info_st support_nic_list[] =
{
  {"Mellanox", 0x19810000, get_mlx_fw_version},
  {"Broadcom", 0x3d110000, get_bcm_fw_version},
};

static int nic_list_size = sizeof(support_nic_list) / sizeof(nic_info_st);

class NicComponent : public Component {
  public:
    NicComponent(string fru, string comp)
      : Component(fru, comp) {}
    int print_version()
    {
      char display_nic_str[128]={0};
      char version[32]={0};
      char vendor[32]={0};
      uint8_t buf[NCSI_DATA_PAYLOAD]={0};
      uint32_t nic_mfg_id=0;
      FILE *file = NULL;
      bool is_unknown_mfg_id = true;
      int current_nic;

      file = fopen(NIC_FW_VER_PATH, "rb");
      if (NULL == file) {
        return FW_STATUS_FAILURE;
      }
      fread(buf, sizeof(uint8_t), NCSI_DATA_PAYLOAD, file);
      fclose(file);
      //get the manufcture id
      nic_mfg_id = (buf[35]<<24) + (buf[34]<<16) + (buf[33]<<8) + buf[32];

      for ( current_nic=0; current_nic <nic_list_size; current_nic++)
      {
        //check the nic on the system is supported or not
        if ( support_nic_list[current_nic].mfg_id == nic_mfg_id )
        {
          sprintf(vendor, support_nic_list[current_nic].mfg_name);
          support_nic_list[current_nic].get_nic_fw(buf, version);
          is_unknown_mfg_id = false;
          break;
        }
        else
        {
          is_unknown_mfg_id = true;
        }
      }

      if ( is_unknown_mfg_id )
      {
        sprintf(display_nic_str ,"NIC firmware version: NA (Unknown Manufacture ID: 0x%04x)", nic_mfg_id);
      }
      else
      {
        sprintf(display_nic_str ,"%s NIC firmware version: %s", vendor, version);
      }
      cout << string(display_nic_str) << endl;
      return FW_STATUS_SUCCESS;
    }
};
NicComponent nic("nic", "nic");

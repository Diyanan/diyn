// raster_shp.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include <io.h>
#include "windows.h"
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include "SieveFilter.h"
using namespace std;

#include "gdal_priv.h"  
#include "ogrsf_frmts.h"   
#include "gdal_alg.h"    
#include "cpl_conv.h"

int ImagePolygonize(const char* img_path,const char* outshp_path,const char* pszFormat);
int DeleteNoneFeature(const char* shp_path);
int VectorDelete(const char* pszFile);
int CopyFile(char *SourceFile,char *NewFile);

int main(int argc, char** argv)
{
	string test_folder = argv[1];
	string label_folder = argv[2];
	int count = atoi(argv[3]);

	for (int i=0;i<count;i++)
	{
		cout<<"正在处理第"<<i<<"个.."<<endl;
		stringstream ss;
		ss << i;
		string SrcFile = test_folder + "\\" + "Binary_" + ss.str() + "_0.png";
		string DstFile = test_folder + "\\" + "Binary_" + ss.str() + "_0.tif";
		string Out_shpPath = test_folder + "\\" + "Binary_" + ss.str() + "_0.shp";
		char* pszSrcFile = const_cast<char*>(SrcFile.c_str());
		char* pszDstFile = const_cast<char*>(DstFile.c_str());
		char* out_shpPath = const_cast<char*>(Out_shpPath.c_str());
		
		string Source_path = label_folder+"\\"+"label"+ss.str()+".PGw";
		string Oldname = test_folder + "\\" + "label" + ss.str() + ".PGw";
		string Newname = test_folder + "\\" + "Binary_" + ss.str() + "_0.PGw";

		char* source_path = const_cast<char*>(Source_path.c_str());
		char* newname = const_cast<char*>(Newname.c_str());
		if((_access(pszSrcFile,0)) != -1)
		{	
			CopyFile(source_path,newname);	

			SmallpatchSieveFilter* sf = new SmallpatchSieveFilter();
			sf->SieveFilter(pszSrcFile,pszDstFile,5,4);
			VectorDelete(out_shpPath);
			ImagePolygonize(pszDstFile,out_shpPath,"ESRI Shapefile");
			DeleteNoneFeature(out_shpPath);
		}
	}
	// system("pause");  
	return 0;
}

int ImagePolygonize(const char* img_path,const char* out_path,const char* pszFormat)  
{  
	GDALAllRegister();  
	OGRRegisterAll();
	CPLSetConfigOption("GDAL_FILENAME_IS_UTF8","NO");  

	GDALDataset* poSrcDS=(GDALDataset*)GDALOpen(img_path,GA_ReadOnly);  
	if(poSrcDS==NULL)  
	{  
		return 0;  
	}

	OGRSFDriver *poDriver;  
	poDriver = OGRSFDriverRegistrar::GetRegistrar()->GetDriverByName( pszFormat );  
	if (poDriver == NULL)  
	{    
		cout<<"error.."<<endl;
		return 0;  
	}  

	OGRDataSource* poDstDS=poDriver->CreateDataSource(out_path);  
	if (poDstDS==NULL)  
	{  
		return 0;  
	}  
 
	OGRSpatialReference *poSpatialRef = new OGRSpatialReference(poSrcDS->GetProjectionRef());  
	OGRLayer* poLayer = poDstDS->CreateLayer("Result", poSpatialRef, wkbPolygon, NULL);  
	if (poDstDS == NULL)   
	{  
		GDALClose((GDALDatasetH)poSrcDS);   
		OGRDataSource::DestroyDataSource(poDstDS);   
		delete poSpatialRef;   
		poSpatialRef = NULL;   
		return 0;  
	}  
	OGRFieldDefn ofieldDef("Segment", OFTInteger);  
	poLayer->CreateField(&ofieldDef);  
	GDALRasterBandH hSrcBand = (GDALRasterBandH) poSrcDS->GetRasterBand(1);  
	GDALPolygonize(hSrcBand, NULL, (OGRLayerH)poLayer, 0, NULL, NULL, NULL); 
	GDALClose(poSrcDS);  
	OGRDataSource::DestroyDataSource(poDstDS);  
	return 1;
}  

int DeleteNoneFeature(const char* shp_path)
{
	GDALAllRegister();  
	OGRRegisterAll(); 
	CPLSetConfigOption("GDAL_FILENAME_IS_UTF8","NO");

	OGRSFDriver *poDriver;  
	poDriver = OGRSFDriverRegistrar::GetRegistrar()->GetDriverByName("ESRI Shapefile");  
	if (poDriver == NULL)  
	{    
	    cout<<"error..."<<endl;
		return 0;  
	}  
	OGRDataSource *poDstDS;
	poDstDS = OGRSFDriverRegistrar::Open(shp_path, true );
	if (poDstDS==NULL)
	{
		return 0;  
	}
	OGRLayer  *poLayer;
	poLayer = poDstDS->GetLayer(0);		
	int fetureCount = poLayer->GetFeatureCount();
	if (fetureCount==0)
	{
		cout<<"Feature is NULL !.\n%s";
		return 0;
	}
	OGRFeatureDefn *pFeatureDefn = NULL;
	pFeatureDefn = poLayer->GetLayerDefn();
	std::string strLayerName = pFeatureDefn->GetName();
	
	OGRFeature *poFeature;
	poLayer->ResetReading();
	while((poFeature = poLayer->GetNextFeature()) != NULL )  
	{
		if (poFeature->GetFieldAsInteger("Segment")==0)
		{
			int index = poFeature->GetFID(); 
			poLayer->DeleteFeature(index);
		}
	}
	// 此句非常关键，如果只用DeleteFeature只是把dbf文件里FID为该值的要素标记为deleted，但实际上并未将该feature真正删除，利用REPACK命令，将忽略标记为deleted的feature。
	std::string strSQL = "REPACK " + strLayerName;
	poDstDS->ExecuteSQL(strSQL.c_str(),NULL,"");
	OGRDataSource::DestroyDataSource(poDstDS);

	return 1;
}

int VectorDelete(const char* pszFile)  
{  
	OGRRegisterAll();  

	//打开矢量  
	OGRDataSource *poDS = OGRSFDriverRegistrar::Open(pszFile, FALSE );  
	if( poDS == NULL )  
		return remove(pszFile);  

	OGRSFDriver *poDriver = poDS->GetDriver();  
	if( poDriver == NULL )  
	{  
		OGRDataSource::DestroyDataSource( poDS );  
		return remove(pszFile);  
	}  

	OGRDataSource::DestroyDataSource( poDS );  
	if(poDriver->DeleteDataSource(pszFile) == OGRERR_NONE)  
		return TRUE;  
	else  
		return remove(pszFile);  
}  

int CopyFile(char *SourceFile,char *NewFile)
{
	ifstream in;
	ofstream out;
	in.open(SourceFile,ios::binary);//打开源文件
	if(in.fail()) //打开源文件失败
	{
		cout<<"Error 1: Fail to open the source file."<<endl;
		in.close();
		out.close();
		return 0;
	}
	out.open(NewFile,ios::binary);//创建目标文件 
	if(out.fail())  //创建文件失败
	{
		cout<<"Error 2: Fail to create the new file."<<endl;
		out.close();
		in.close();
		return 0;
	}
	else   //复制文件
	{	
		out<<in.rdbuf();
		out.close();
		in.close();
		return 1;
	}
}
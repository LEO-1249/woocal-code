function  suc = Dcm2VarPar(DCMPath, A2LPath, VarOrPar)
% Brief: ��DCM�еı궨����ֵд�뵽Matlab��Var����Parameter��
%       
% Param: 
%         DCMPath   - Dcm File Path
%         A2yLPath   - A2L File Path
%         VarOrPar  - Dcm to Var or Dcm to Parameter('Var' or 'Parameter')
% Return: 
%         1 - executed successfully
%         0 - fail executed
%       
% Call this: 
% 
% Copyright(C) 2018-2028, Suzhou National Square Automotive Electronics.
% 
% Author: WL BAO
%  
 
%% Initial
if isempty(DCMPath)
    [fileName, filePath] = uigetfile('*.dcm', '��ѡ��DCM�ļ�');
    DCMPath = fullfile(filePath, fileName);
end

if isempty(A2LPath)
    [fileName, filePath] = uigetfile('*.a2l', '��ѡ��A2L�ļ�');
    A2LPath = fullfile(filePath, fileName);
end

suc = 0;
%%
%demo
%A2LPath = 'C:\Users/baoweiliang\Desktop\�½��ļ���\DCRS_FrameModel_TorqueStructure_vld.a2l';
%A2LPath = 'C:\Users/baoweiliang\Desktop\�½��ļ���\DCRS_FrameModel_TorqueStructure_vld.a2l';
%VarOrPar = 'Var';
%Dcm2VarPar(DCMPath, A2LPath, VarOrPar);
%%
DcmInfo = py.DcmInfGet.GetDcmInf(DCMPath, A2LPath);
if strcmp(VarOrPar, 'Var') == 1
    for i = 1:length(DcmInfo)
        name = char(DcmInfo{i}{1});
        Cell_value = cell(DcmInfo{i}{2});
        value=[];
        
        for j = 1:length(Cell_value)
            value(1, j) = Cell_value{j};
        end

    %     eval([name,'=value;']);
        assignin('base', name, value);
    end

elseif strcmp(VarOrPar, 'Parameter') == 1
        for i = 1:length(DcmInfo)
            name = char(DcmInfo{i}{1});
            Cell_value = cell(DcmInfo{i}{2});
            tempPara = Calibration.Parameter;
            tempPara.DocUnits = char(DcmInfo{i}{4});
            tempPara.Description = char(DcmInfo{i}{3}); 
            tempPara.Value = [];
            for j = 1:length(Cell_value)
               tempPara.Value(1, j) = Cell_value{j};
            end
            assignin('base', name, tempPara);
        end
end
suc = 1;
end